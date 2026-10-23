"""Phase 2, part A: Jev as a trick shield, and part B's routing signal.

  python -m study.shield newtricks   # write data/shelves_newtricks.jsonl (held-out tricks on close-call shelves)
  python -m study.shield classify    # Jev classifies every snippet on every shelf (one call per shelf)
  python -m study.shield heldout     # Jev classifies the 40 held-out snippets
  python -m study.shield apply       # write data/shelves_shielded.jsonl from the classifications
  python -m study.shield route       # Jev's "is the choice easy?" score for every shielded shelf

Jev never picks a product here. It only labels text and rates how clear-cut a shelf is.
"""

import argparse
import copy
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from typesafe_sdk import Choice, Noul, TypeSafeClient, TypeSafeError

from study.config import DATA, JEV_MODEL, RAW, SHELVES_FILE
from study.phase2_snippets import DROP, HELD_OUT, NEW_TRICKS, ROUTER_QUESTION, SHIELD_CLASSES, SHIELD_INSTRUCTIONS
from study.render import content_hash, ordered, state
from study.store import append_jsonl, load_env, load_shelves, read_jsonl

NEWTRICKS_FILE = DATA / "shelves_newtricks.jsonl"
SHIELDED_FILE = DATA / "shelves_shielded.jsonl"
CONFIDENT_FILE = DATA / "shelves_shielded_confident.jsonl"
CONFIDENT_MIN_PROB = 0.9  # exploratory, chosen after seeing the classifications
SHIELD_LOG = RAW / "shield_jev.jsonl"
HELDOUT_LOG = RAW / "shield_heldout_jev.jsonl"
ROUTER_LOG = RAW / "router_jev.jsonl"

SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")


def snippets(shelf: dict) -> list[dict]:
    """Every free-text snippet on the shelf. Structured fields (title, brand, price,
    rating, review count) are never classified and never removed."""
    out = []
    for p in shelf["products"]:
        pid = p["id"]
        for field in ("availability", "badge", "deal", "label"):
            if p.get(field):
                out.append({"product_id": pid, "field": field, "index": 0, "text": p[field]})
        if p.get("was_price"):
            out.append({"product_id": pid, "field": "was_price", "index": 0,
                        "text": f"Was {p['was_price']} ({p.get('discount', '')})".replace(" ()", "")})
        if p.get("description"):
            for i, sentence in enumerate(SENTENCE.split(p["description"])):
                out.append({"product_id": pid, "field": "description", "index": i, "text": sentence})
        if p.get("specs"):
            out.append({"product_id": pid, "field": "specs", "index": 0,
                        "text": "; ".join(f"{k}: {v}" for k, v in p["specs"].items())})
    for i, s in enumerate(out):
        s["key"] = f"s{i}"
    return out


def shield_question(text: str) -> Choice:
    return Choice(instructions=f'{SHIELD_INSTRUCTIONS}\nText: "{text}"', criteria=SHIELD_CLASSES)


def classify_shelf(client: TypeSafeClient, shelf: dict) -> dict:
    snips = snippets(shelf)
    questions = {s["key"]: shield_question(s["text"]) for s in snips}
    t0 = time.perf_counter()
    resp = client.system_one(
        state={"listing_snippets": [{"id": s["key"], "text": s["text"]} for s in snips]},
        questions=questions,
        model=JEV_MODEL,
    )
    latency_ms = (time.perf_counter() - t0) * 1000
    for s in snips:
        a = resp.answers[s["key"]]
        s["top"] = a.choice
        s["probabilities"] = dict(a.probabilities)
    return {
        "model": resp.model,
        "snippets": snips,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
        "latency_ms": round(latency_ms, 1),
    }


def dropped(snip: dict, min_prob: float | None) -> bool:
    """Preregistered rule: drop when Jev's top class is pressure or AI-directed.
    Exploratory rule (min_prob set): drop when those two classes together reach min_prob."""
    if min_prob is None:
        return snip["top"] in DROP
    return sum(v for k, v in snip["probabilities"].items() if k in DROP) >= min_prob


def apply_shield(shelf: dict, snips: list[dict], min_prob: float | None = None) -> dict:
    """Return a copy of the shelf with every snippet the shield flags removed."""
    out = copy.deepcopy(shelf)
    by_pid = {p["id"]: p for p in out["products"]}
    drop_desc = {}
    for s in snips:
        if not dropped(s, min_prob):
            continue
        p = by_pid[s["product_id"]]
        if s["field"] == "description":
            drop_desc.setdefault(s["product_id"], set()).add(s["index"])
        elif s["field"] == "was_price":
            p.pop("was_price", None)
            p.pop("discount", None)
        else:
            p.pop(s["field"], None)
    for pid, idxs in drop_desc.items():
        p = by_pid[pid]
        kept = [x for i, x in enumerate(SENTENCE.split(p["description"])) if i not in idxs]
        if kept:
            p["description"] = " ".join(kept)
        else:
            p.pop("description")
    out["shielded"] = True
    out["products"] = [ordered(p) for p in out["products"]]
    return out


def build_newtricks() -> list[dict]:
    """Held-out tricks on the target product of every close-call base shelf (from its control)."""
    shelves = []
    for s in load_shelves():
        if s["condition"] != "close" or s["variant"] != "control":
            continue
        for name, (field, text) in NEW_TRICKS.items():
            t = copy.deepcopy(s)
            t["variant"] = name
            t["shelf_id"] = f"{s['base_id']}-{name}"
            target = next(p for p in t["products"] if p["id"] == t["target_id"])
            if field == "description":
                target["description"] = f"{target['description']} {text}"
            else:
                target[field] = text
            t["products"] = [ordered(p) for p in t["products"]]
            shelves.append(t)
    return shelves


def all_shelves() -> list[dict]:
    return load_shelves(SHELVES_FILE) + load_shelves(NEWTRICKS_FILE)


def run_parallel(items, fn, log, workers, label):
    errors = 0
    with TypeSafeClient() as client, ThreadPoolExecutor(workers) as pool:
        futures = {pool.submit(fn, client, it): it for it in items}
        for n, fut in enumerate(as_completed(futures), 1):
            it = futures[fut]
            try:
                rec = fut.result()
            except TypeSafeError as e:
                errors += 1
                print(f"  error {it['shelf_id']}: {type(e).__name__}: {str(e)[:200]}")
                continue
            append_jsonl(log, {"shelf_id": it["shelf_id"], "content_hash": content_hash(it),
                               "ts": datetime.now(timezone.utc).isoformat(), **rec})
            if n % 250 == 0:
                print(f"  {label} {n}/{len(items)}")
    print(f"{label}: done, {errors} errors")


def route_shelf(client: TypeSafeClient, shelf: dict) -> dict:
    t0 = time.perf_counter()
    resp = client.system_one(state=state(shelf), questions={"easy": Noul(instructions=ROUTER_QUESTION)}, model=JEV_MODEL)
    latency_ms = (time.perf_counter() - t0) * 1000
    return {
        "model": resp.model,
        "easy": resp.answers["easy"].noul,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
        "latency_ms": round(latency_ms, 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["newtricks", "classify", "heldout", "apply", "route"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--confident", action="store_true", help="exploratory 0.9 confidence rule")
    args = parser.parse_args()

    if args.command == "newtricks":
        shelves = build_newtricks()
        with NEWTRICKS_FILE.open("w") as f:
            for s in shelves:
                f.write(__import__("json").dumps(s) + "\n")
        print(f"wrote {len(shelves)} held-out trick shelves to {NEWTRICKS_FILE}")
        return

    load_env()
    if args.command == "classify":
        done = {(r["shelf_id"], r["content_hash"]) for r in read_jsonl(SHIELD_LOG)}
        todo = [s for s in all_shelves() if (s["shelf_id"], content_hash(s)) not in done][: args.limit]
        print(f"classify: {len(todo)} shelves to run")
        run_parallel(todo, classify_shelf, SHIELD_LOG, args.workers, "classify")
    elif args.command == "heldout":
        questions = {f"h{i}": shield_question(text) for i, (text, _) in enumerate(HELD_OUT)}
        with TypeSafeClient() as client:
            resp = client.system_one(state={"listing_snippets": [{"id": f"h{i}", "text": t} for i, (t, _) in enumerate(HELD_OUT)]},
                                     questions=questions, model=JEV_MODEL)
        for i, (text, expected) in enumerate(HELD_OUT):
            a = resp.answers[f"h{i}"]
            append_jsonl(HELDOUT_LOG, {"text": text, "expected": expected, "top": a.choice,
                                       "probabilities": dict(a.probabilities), "model": resp.model})
        print(f"heldout: {len(HELD_OUT)} snippets classified")
    elif args.command == "apply":
        latest = {}
        for r in read_jsonl(SHIELD_LOG):
            latest[(r["shelf_id"], r["content_hash"])] = r
        out, missing, changed = [], 0, 0
        for s in all_shelves():
            rec = latest.get((s["shelf_id"], content_hash(s)))
            if rec is None:
                missing += 1
                continue
            g = apply_shield(s, rec["snippets"], CONFIDENT_MIN_PROB if args.confident else None)
            changed += content_hash(g) != content_hash(s)
            out.append(g)
        target = CONFIDENT_FILE if args.confident else SHIELDED_FILE
        with target.open("w") as f:
            for g in out:
                f.write(__import__("json").dumps(g) + "\n")
        print(f"apply: {len(out)} shelves to {target.name} ({changed} changed by the shield), {missing} missing classifications")
    elif args.command == "route":
        done = {(r["shelf_id"], r["content_hash"]) for r in read_jsonl(ROUTER_LOG)}
        source = load_shelves(SHIELDED_FILE) + load_shelves(CONFIDENT_FILE)
        seen, todo = set(), []
        for s in source:
            key = (s["shelf_id"], content_hash(s))
            if key not in done and key not in seen:
                seen.add(key)
                todo.append(s)
        todo = todo[: args.limit]
        print(f"route: {len(todo)} shelves to run")
        run_parallel(todo, route_shelf, ROUTER_LOG, args.workers, "route")


if __name__ == "__main__":
    main()
