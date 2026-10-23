"""Ask GPT and Gemini (through OpenRouter) to pick a product on every shelf.

Same instructions, same shelf JSON and the same one-field JSON answer as the
Claude runner. Each shelf is sampled several times at default sampling settings.

Run: python -m study.run_openrouter --tag pilot --models gpt,gemini --categories kettle,headphones --replicates 2
"""

import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import httpx2 as httpx

from study.cli import add_filters
from study.config import AGENT_INSTRUCTIONS, OPENROUTER_EFFORT, OPENROUTER_MODELS, RAW
from study.render import claude_user_message, content_hash, product_ids, request_key
from study.store import append_jsonl, load_env, load_shelves, read_jsonl, select

URL = "https://openrouter.ai/api/v1/chat/completions"
SCHEMA = {
    "type": "object",
    "properties": {"product_id": {"type": "string"}},
    "required": ["product_id"],
    "additionalProperties": False,
}


def out_path(alias: str):
    return RAW / f"openrouter_{alias}.jsonl"


def body(slug: str, shelf: dict) -> dict:
    return {
        "model": slug,
        "messages": [
            {"role": "system", "content": AGENT_INSTRUCTIONS},
            {"role": "user", "content": claude_user_message(shelf)},
        ],
        "response_format": {"type": "json_schema", "json_schema": {"name": "pick", "strict": True, "schema": SCHEMA}},
        "reasoning": {"effort": OPENROUTER_EFFORT},
        # Only route to providers that honour the JSON schema and reasoning settings.
        "provider": {"require_parameters": True},
        "usage": {"include": True},
    }


def call(client: httpx.Client, alias: str, shelf: dict) -> dict:
    t0 = time.perf_counter()
    r = client.post(URL, json=body(OPENROUTER_MODELS[alias], shelf))
    latency_ms = (time.perf_counter() - t0) * 1000
    r.raise_for_status()
    d = r.json()
    if "error" in d:
        raise RuntimeError(json.dumps(d["error"])[:300])
    choice = d["choices"][0]
    usage = d.get("usage") or {}
    rec = {
        "model": d.get("model"),
        "provider": d.get("provider"),
        "finish_reason": choice.get("finish_reason"),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
        "cost_usd": usage.get("cost"),
        "latency_ms": round(latency_ms, 1),
        "choice": None,
        "valid": False,
    }
    text = choice["message"].get("content") or ""
    try:
        rec["choice"] = json.loads(text).get("product_id")
    except (json.JSONDecodeError, AttributeError):
        rec["raw_text"] = text[:500]
    rec["valid"] = rec["choice"] in product_ids(shelf)
    return rec


def main() -> None:
    parser = argparse.ArgumentParser()
    add_filters(parser)
    parser.add_argument("--models", type=lambda s: s.split(","), default=list(OPENROUTER_MODELS))
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    load_env()
    shelves = select(load_shelves(), args.categories, args.replicates, args.variants, args.limit,
                    args.conditions)
    jobs = []
    for alias in args.models:
        done = {r["key"] for r in read_jsonl(out_path(alias))}
        for shelf in shelves:
            for sample in range(args.samples):
                if request_key(alias, shelf, sample, args.tag) not in done:
                    jobs.append((alias, shelf, sample))
    print(f"openrouter: {len(shelves)} shelves x {args.samples} samples x {len(args.models)} models, {len(jobs)} pending")

    headers = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}
    errors = 0
    with httpx.Client(headers=headers, timeout=180) as client, ThreadPoolExecutor(args.workers) as pool:
        futures = {pool.submit(call, client, alias, shelf): (alias, shelf, sample) for alias, shelf, sample in jobs}
        for n, fut in enumerate(as_completed(futures), 1):
            alias, shelf, sample = futures[fut]
            try:
                result = fut.result()
            except (httpx.HTTPError, RuntimeError, KeyError) as e:
                errors += 1
                print(f"  error {alias} {shelf['shelf_id']}: {type(e).__name__}: {str(e)[:200]}")
                continue
            append_jsonl(out_path(alias), {
                "key": request_key(alias, shelf, sample, args.tag),
                "content_hash": content_hash(shelf),
                "tag": args.tag,
                "mode": "choice",
                "model_alias": alias,
                "shelf_id": shelf["shelf_id"],
                "sample": sample,
                "ts": datetime.now(timezone.utc).isoformat(),
                **result,
            })
            if n % 50 == 0:
                print(f"  {n}/{len(jobs)}")
    print(f"openrouter: done, {errors} errors (rerun to retry)")


if __name__ == "__main__":
    main()
