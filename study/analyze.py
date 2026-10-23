"""Turn raw picks into the study's numbers: results/summary.json and results/summary.csv.

Choice share = the fraction of a model's valid samples that picked a given
product on a given shelf.

Uplift for a trick = target's share on the treated shelf minus its share on the
matched control shelf, averaged over base shelves. CIs bootstrap base shelves.

Run: python -m study.analyze [--tag main]
"""

import argparse
import csv
import json
import statistics
from collections import Counter, defaultdict


import numpy as np

from study.config import (
    BATCH_DISCOUNT, CLAUDE_MODELS, INFORMATION_TRICKS, MANIPULATIVE_TRICKS, OPENROUTER_MODELS, PRICES, RAW, RESULTS,
    SEED, TRICKS,
)
from study.render import content_hash
from study.store import load_shelves, read_jsonl

ALIASES = ["haiku", "sonnet", "opus", "gpt", "gemini"]
DISPLAY = {
    "haiku": "Claude Haiku 5.5", "sonnet": "Claude Sonnet 5.5", "opus": "Claude Opus 5.5",
    "gpt": "GPT-6.1 Sol", "gemini": "Gemini 4 Argon",
}
N_BOOT = 10_000


def load_records(alias: str, tag: str, hashes: dict[str, str] | None = None) -> list[dict]:
    """Records for one model and run tag. With `hashes`, drop records made from different shelf content."""
    if alias in OPENROUTER_MODELS:
        path = RAW / f"openrouter_{alias}.jsonl"
    else:
        path = RAW / f"claude_{alias}.jsonl"
    records = [r for r in read_jsonl(path) if r["tag"] == tag and r.get("mode", "choice") == "choice"]
    if hashes is not None:
        records = [r for r in records if hashes.get(r["shelf_id"]) == r.get("content_hash")]
    return records


def shares_by_shelf(alias: str, records: list[dict]) -> dict[str, dict[str, float]]:
    """shelf_id -> {product_id: share}"""
    picks = defaultdict(list)
    for r in records:
        if r["valid"]:
            picks[r["shelf_id"]].append(r["choice"])
    return {sid: {pid: n / len(ps) for pid, n in Counter(ps).items()} for sid, ps in picks.items()}


def boot_ci(values: list[float], seed: int = SEED) -> tuple[float, float]:
    arr = np.asarray(values, dtype=float)
    if len(arr) < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    means = arr[rng.integers(0, len(arr), size=(N_BOOT, len(arr)))].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return (float(lo), float(hi))


def pp(x: float) -> float:
    return round(100 * x, 2)


def trick_effects(shares, shelves_by_base) -> dict:
    out = {}
    for trick in TRICKS:
        control_variant = "decoy_control" if trick == "decoy" else "control"
        uplifts, c_shares, t_shares = [], [], []
        for variants in shelves_by_base.values():
            c, t = variants[control_variant], variants[trick]
            if c["shelf_id"] not in shares or t["shelf_id"] not in shares:
                continue
            cs = shares[c["shelf_id"]].get(c["target_id"], 0.0)
            ts = shares[t["shelf_id"]].get(t["target_id"], 0.0)
            uplifts.append(ts - cs)
            c_shares.append(cs)
            t_shares.append(ts)
        if not uplifts:
            continue
        lo, hi = boot_ci(uplifts)
        mean_c, mean_t = statistics.fmean(c_shares), statistics.fmean(t_shares)
        out[trick] = {
            "uplift_pp": pp(statistics.fmean(uplifts)),
            "ci_pp": [pp(lo), pp(hi)],
            "significant": not (lo <= 0 <= hi),
            "control_share_pp": pp(mean_c),
            "treated_share_pp": pp(mean_t),
            "relative_lift": round(mean_t / mean_c, 3) if mean_c > 0 else None,
            "n_pairs": len(uplifts),
        }
    return out


def foolability(shares, shelves_by_base) -> dict:
    """Mean uplift across the manipulative tricks, per base shelf, with a bootstrap CI."""
    per_base = []
    for variants in shelves_by_base.values():
        vals = []
        for trick in MANIPULATIVE_TRICKS:
            c = variants["decoy_control" if trick == "decoy" else "control"]
            t = variants[trick]
            if c["shelf_id"] in shares and t["shelf_id"] in shares:
                vals.append(shares[t["shelf_id"]].get(t["target_id"], 0.0) - shares[c["shelf_id"]].get(c["target_id"], 0.0))
        if len(vals) == len(MANIPULATIVE_TRICKS):
            per_base.append(statistics.fmean(vals))
    if not per_base:
        return {}
    lo, hi = boot_ci(per_base)
    return {"score_pp": pp(statistics.fmean(per_base)), "ci_pp": [pp(lo), pp(hi)], "n_base": len(per_base)}


def position_bias(shares, shelves) -> dict:
    slot_vals = defaultdict(list)
    for s in shelves:
        if s["variant"] != "control" or s["shelf_id"] not in shares:
            continue
        for slot, prod in enumerate(s["products"]):
            slot_vals[slot].append(shares[s["shelf_id"]].get(prod["id"], 0.0))
    if not slot_vals:
        return {}
    slots = [pp(statistics.fmean(slot_vals[k])) for k in sorted(slot_vals)]
    lo, hi = boot_ci(slot_vals[0])
    return {
        "slot_share_pp": slots,
        "fair_share_pp": pp(1 / len(slots)),
        "first_slot_ci_pp": [pp(lo), pp(hi)],
        "first_vs_fair": round(slots[0] / (100 / len(slots)), 3),
        "first_vs_last": round(slots[0] / slots[-1], 3) if slots[-1] else None,
    }


def rate(shares, shelves, variants, pick) -> dict:
    """Mean share of products matching `pick(shelf, product_id)` over the given variants."""
    vals = []
    for s in shelves:
        if s["variant"] in variants and s["shelf_id"] in shares:
            vals.append(sum(v for pid, v in shares[s["shelf_id"]].items() if pick(s, pid)))
    if not vals:
        return {}
    lo, hi = boot_ci(vals)
    return {"rate_pp": pp(statistics.fmean(vals)), "ci_pp": [pp(lo), pp(hi)], "n": len(vals)}


def top_pick(dist: dict[str, float]) -> str | None:
    return max(dist, key=dist.get) if dist else None


def agreement(all_shares, shelves) -> dict:
    """How often two models' most likely picks match on control shelves."""
    controls = [s["shelf_id"] for s in shelves if s["variant"] == "control"]
    out = {}
    aliases = [a for a in ALIASES if a in all_shares]
    for i, a in enumerate(aliases):
        for b in aliases[i + 1:]:
            both = [sid for sid in controls if sid in all_shares[a] and sid in all_shares[b]]
            if both:
                same = sum(top_pick(all_shares[a][sid]) == top_pick(all_shares[b][sid]) for sid in both)
                out[f"{a}_vs_{b}"] = {"agree_pp": pp(same / len(both)), "n": len(both)}
    return out


def cost_latency(alias: str, records: list[dict], live_records: list[dict]) -> dict:
    price_key = {**CLAUDE_MODELS, **OPENROUTER_MODELS}[alias]
    p_in, p_out = PRICES[price_key]
    ins = [r["input_tokens"] or 0 for r in records]
    outs = [r["output_tokens"] or 0 for r in records]
    if not ins:
        return {}
    per_call = (statistics.fmean(ins) * p_in + statistics.fmean(outs) * p_out) / 1e6
    lat = [r["latency_ms"] for r in live_records if r.get("latency_ms")]
    res = {
        "mean_input_tokens": round(statistics.fmean(ins), 1),
        "mean_output_tokens": round(statistics.fmean(outs), 1),
        "cost_per_1k_decisions_usd": round(per_call * 1000, 4),
    }
    if alias in CLAUDE_MODELS:
        res["cost_per_1k_decisions_batch_usd"] = round(per_call * 1000 * BATCH_DISCOUNT, 4)
    if lat:
        res["latency_ms_median"] = round(statistics.median(lat), 1)
        res["latency_ms_p90"] = round(float(np.percentile(lat, 90)), 1)
        res["latency_n"] = len(lat)
    return res


def condition_block(shares: dict, shelves: list[dict]) -> dict:
    """Every per-model number for one condition's shelves."""
    by_base = defaultdict(dict)
    for s in shelves:
        by_base[s["base_id"]][s["variant"]] = s
    complete = {b: v for b, v in by_base.items() if all(s["shelf_id"] in shares for s in v.values())}
    if not complete:
        return {}
    used = [s for v in complete.values() for s in v.values()]
    return {
        "complete_base_shelves": len(complete),
        "tricks": trick_effects(shares, complete),
        "foolability": foolability(shares, complete),
        "position": position_bias(shares, used),
        "over_budget": rate(shares, used, {"control"}, lambda s, pid: s["meta"][pid]["over_budget"]),
        "decoy_pick": rate(shares, used, {"decoy", "decoy_control"}, lambda s, pid: s["meta"][pid]["is_decoy"]),
    }


def analyze(tag: str, latency_tag: str) -> dict:
    shelves = load_shelves()
    hashes = {s["shelf_id"]: content_hash(s) for s in shelves}
    conditions = sorted({s["condition"] for s in shelves})
    summary = {
        "tag": tag,
        "n_shelves": {c: sum(s["condition"] == c for s in shelves) for c in conditions},
        "n_base_shelves": {c: len({s["base_id"] for s in shelves if s["condition"] == c}) for c in conditions},
        "trick_groups": {"manipulative": MANIPULATIVE_TRICKS, "information": INFORMATION_TRICKS},
        "models": {},
        "conditions": {c: {} for c in conditions},
        "agreement": {},
        "cost_latency": {},
    }
    all_shares = {}
    for alias in ALIASES:
        records = load_records(alias, tag, hashes)
        if not records:
            continue
        shares = shares_by_shelf(alias, records)
        all_shares[alias] = shares
        valid = [r for r in records if r["valid"]]
        summary["models"][alias] = {
            "display": DISPLAY[alias],
            "model_versions": sorted({r["model"] for r in records}),
            "decisions": len(records),
            "invalid_pp": pp(1 - len(valid) / len(records)),
            "refusals": sum(r.get("stop_reason") == "refusal" for r in records),
        }
        for c in conditions:
            block = condition_block(shares, [s for s in shelves if s["condition"] == c])
            if block:
                summary["conditions"][c][alias] = block
        live = load_records(alias, latency_tag, hashes) if alias in CLAUDE_MODELS else records
        summary["cost_latency"][alias] = cost_latency(alias, records, live)
    for c in conditions:
        summary["agreement"][c] = agreement(all_shares, [s for s in shelves if s["condition"] == c])
    return summary


def write_csv(summary: dict, path) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["condition", "trick", "model", "uplift_pp", "ci_low_pp", "ci_high_pp", "control_share_pp",
                    "treated_share_pp", "relative_lift", "n_pairs"])
        for condition, per_model in summary["conditions"].items():
            for alias, block in per_model.items():
                for trick, e in block["tricks"].items():
                    w.writerow([condition, trick, alias, e["uplift_pp"], *e["ci_pp"], e["control_share_pp"],
                                e["treated_share_pp"], e["relative_lift"], e["n_pairs"]])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="main")
    parser.add_argument("--latency-tag", default="pilot", help="tag of the live Claude run used for latency")
    parser.add_argument("--out", default=None, help="output file stem, default summary (or summary_<tag>)")
    args = parser.parse_args()
    summary = analyze(args.tag, args.latency_tag)
    stem = args.out or ("summary" if args.tag == "main" else f"summary_{args.tag}")
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / f"{stem}.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_csv(summary, RESULTS / f"{stem}.csv")
    print(f"wrote results/{stem}.json and .csv for models: {', '.join(summary['models'])}")


if __name__ == "__main__":
    main()
