"""Ask Claude models to pick a product on every shelf.

Claude returns one pick per call, so each shelf is sampled several times and
the choice share is measured from those samples.

  live     direct calls (used for the pilot and for latency numbers)
  submit   send the run to the Message Batches API (half price)
  collect  wait for submitted batches and save their results
  reasons  small live run that also asks for a one-line reason (for quotes)

Run:
  python -m study.run_claude live --tag pilot --models haiku,sonnet,opus --categories kettle,headphones --replicates 2
  python -m study.run_claude submit --models haiku,sonnet,opus --samples 3
  python -m study.run_claude collect
"""

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

from study.cli import add_filters
from study.config import AGENT_INSTRUCTIONS, CLAUDE_EFFORT, CLAUDE_MAX_TOKENS, CLAUDE_MODELS, RAW
from study.render import claude_user_message, content_hash, product_ids, request_key
from pathlib import Path

from study.config import SHELVES_FILE
from study.store import append_jsonl, load_env, load_shelves, read_jsonl, reuse_index, reused, select

BATCHES = RAW / "claude_batches.jsonl"

# One fixed schema for every request so the compiled grammar is reused.
# Picks are validated against the shelf afterwards.
CHOICE_SCHEMA = {
    "type": "object",
    "properties": {"product_id": {"type": "string"}},
    "required": ["product_id"],
    "additionalProperties": False,
}
REASON_SCHEMA = {
    "type": "object",
    "properties": {
        "product_id": {"type": "string"},
        "reason": {"type": "string", "description": "One short sentence explaining the pick."},
    },
    "required": ["product_id", "reason"],
    "additionalProperties": False,
}


def out_path(alias: str):
    return RAW / f"claude_{alias}.jsonl"


def params(model: str, shelf: dict, schema: dict = CHOICE_SCHEMA) -> dict:
    # No refusal fallback on purpose: a fallback would silently swap in another
    # model and mix it into this model's results. Refusals are recorded instead.
    return {
        "model": model,
        "max_tokens": CLAUDE_MAX_TOKENS,
        "system": AGENT_INSTRUCTIONS,
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": CLAUDE_EFFORT, "format": {"type": "json_schema", "schema": schema}},
        "messages": [{"role": "user", "content": claude_user_message(shelf)}],
    }


def parse(message, shelf: dict) -> dict:
    """Pull the pick out of a Message. Never raises: bad answers are recorded as such."""
    rec = {
        "model": message.model,
        "stop_reason": message.stop_reason,
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
        "choice": None,
        "reason": None,
        "valid": False,
    }
    if message.stop_reason == "refusal":
        rec["refusal_category"] = getattr(message.stop_details, "category", None)
        return rec
    text = next((b.text for b in message.content if b.type == "text"), "")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        rec["raw_text"] = text[:500]
        return rec
    rec["choice"] = data.get("product_id")
    rec["reason"] = data.get("reason")
    rec["valid"] = rec["choice"] in product_ids(shelf)
    return rec


def record(alias: str, shelf: dict, sample: int, tag: str, mode: str, result: dict) -> dict:
    return {
        "key": request_key(alias, shelf, sample, tag, mode),
        "content_hash": content_hash(shelf),
        "tag": tag,
        "mode": mode,
        "model_alias": alias,
        "shelf_id": shelf["shelf_id"],
        "sample": sample,
        "ts": datetime.now(timezone.utc).isoformat(),
        **result,
    }


def pending_jobs(shelves, aliases, samples, tag, mode):
    """Jobs still to run. An earlier answer to byte-identical input (any run) is copied instead."""
    jobs, copied, deferred, queued = [], 0, 0, set()
    for alias in aliases:
        existing = read_jsonl(out_path(alias))
        done = {r["key"] for r in existing}
        idx = reuse_index(existing)
        for shelf in shelves:
            for sample in range(samples):
                key = request_key(alias, shelf, sample, tag, mode)
                if key in done:
                    continue
                prior = idx.get((content_hash(shelf), sample, mode))
                if prior is not None:
                    append_jsonl(out_path(alias), reused(prior, key, tag, shelf["shelf_id"]))
                    done.add(key)
                    copied += 1
                elif (alias, content_hash(shelf), sample) not in queued:
                    queued.add((alias, content_hash(shelf), sample))
                    jobs.append((alias, shelf, sample))
                else:
                    deferred += 1  # same input already queued: copied on the next run
    if copied or deferred:
        print(f"reused {copied} earlier answers to identical shelves; {deferred} duplicates wait for a rerun")
    return jobs


def run_live(client, jobs, tag, mode, schema, workers):
    def call(alias, shelf, sample):
        t0 = time.perf_counter()
        msg = client.messages.create(**params(CLAUDE_MODELS[alias], shelf, schema))
        latency_ms = (time.perf_counter() - t0) * 1000
        return {**parse(msg, shelf), "latency_ms": round(latency_ms, 1)}

    errors = 0
    with ThreadPoolExecutor(workers) as pool:
        futures = {pool.submit(call, *job): job for job in jobs}
        for n, fut in enumerate(as_completed(futures), 1):
            alias, shelf, sample = futures[fut]
            try:
                result = fut.result()
            except anthropic.RateLimitError:
                errors += 1
                print(f"  rate limited: {alias} {shelf['shelf_id']} (rerun to retry)")
                continue
            except anthropic.APIStatusError as e:
                errors += 1
                print(f"  API error {e.status_code}: {alias} {shelf['shelf_id']}: {str(e)[:200]}")
                continue
            except anthropic.APIConnectionError:
                errors += 1
                print(f"  connection error: {alias} {shelf['shelf_id']} (rerun to retry)")
                continue
            append_jsonl(out_path(alias), record(alias, shelf, sample, tag, mode, result))
            if n % 50 == 0:
                print(f"  {n}/{len(jobs)}")
    print(f"live: done, {errors} errors")


def submit(client, jobs, tag, shelves_file):
    by_alias = {}
    for alias, shelf, sample in jobs:
        by_alias.setdefault(alias, []).append((shelf, sample))
    for alias, items in by_alias.items():
        mapping, requests = {}, []
        for shelf, sample in items:
            key = request_key(alias, shelf, sample, tag, "choice")
            custom_id = f"{alias}-{key}"
            mapping[custom_id] = {"shelf_id": shelf["shelf_id"], "sample": sample}
            requests.append(Request(
                custom_id=custom_id,
                params=MessageCreateParamsNonStreaming(**params(CLAUDE_MODELS[alias], shelf)),
            ))
        batch = client.messages.batches.create(requests=requests)
        append_jsonl(BATCHES, {"batch_id": batch.id, "alias": alias, "tag": tag, "requests": mapping,
                               "shelves_file": str(shelves_file),
                               "collected": False, "ts": datetime.now(timezone.utc).isoformat()})
        print(f"submitted {alias}: {len(requests)} requests, batch {batch.id}")


def collect(client, poll_seconds):
    batches = read_jsonl(BATCHES)
    collected = {b["batch_id"] for b in batches if b.get("collected")}
    open_batches = [b for b in batches if not b.get("collected") and b["batch_id"] not in collected]
    for b in open_batches:
        while True:
            status = client.messages.batches.retrieve(b["batch_id"])
            if status.processing_status == "ended":
                break
            c = status.request_counts
            print(f"  {b['alias']} {b['batch_id']}: processing {c.processing}, done {c.succeeded}, errored {c.errored}")
            time.sleep(poll_seconds)
        shelves_by_id = {s["shelf_id"]: s for s in load_shelves(Path(b.get("shelves_file", SHELVES_FILE)))}
        done = {r["key"] for r in read_jsonl(out_path(b["alias"]))}
        counts = {"succeeded": 0, "errored": 0, "canceled": 0, "expired": 0}
        for res in client.messages.batches.results(b["batch_id"]):
            counts[res.result.type] += 1
            if res.result.type != "succeeded":
                continue
            info = b["requests"][res.custom_id]
            shelf = shelves_by_id[info["shelf_id"]]
            rec = record(b["alias"], shelf, info["sample"], b["tag"], "choice", parse(res.result.message, shelf))
            if rec["key"] not in done:
                append_jsonl(out_path(b["alias"]), rec)
        append_jsonl(BATCHES, {**b, "requests": {}, "collected": True, "counts": counts})
        print(f"collected {b['alias']} {b['batch_id']}: {counts}")
    if not open_batches:
        print("no open batches")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["live", "submit", "collect", "reasons"])
    add_filters(parser)
    parser.add_argument("--models", type=lambda s: s.split(","), default=list(CLAUDE_MODELS))
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--poll-seconds", type=int, default=60)
    args = parser.parse_args()

    load_env()
    client = anthropic.Anthropic()
    shelves_file = Path(args.shelves_file) if args.shelves_file else SHELVES_FILE
    all_shelves = load_shelves(shelves_file)

    if args.command == "collect":
        collect(client, args.poll_seconds)
        return

    shelves = select(all_shelves, args.categories, args.replicates, args.variants, args.limit,
                    args.conditions)
    mode = "reasons" if args.command == "reasons" else "choice"
    jobs = pending_jobs(shelves, args.models, args.samples, args.tag, mode)
    print(f"{args.command}: {len(shelves)} shelves x {args.samples} samples x {len(args.models)} models, {len(jobs)} pending")
    if not jobs:
        return
    if args.command == "submit":
        submit(client, jobs, args.tag, shelves_file)
    else:
        schema = REASON_SCHEMA if mode == "reasons" else CHOICE_SCHEMA
        run_live(client, jobs, args.tag, mode, schema, args.workers)


if __name__ == "__main__":
    main()
