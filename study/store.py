"""Read shelves and append-only JSONL result logs."""

import json
from pathlib import Path

from study.config import SHELVES_FILE


def load_shelves(path: Path = SHELVES_FILE) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f]


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def select(shelves: list[dict], categories=None, replicates=None, variants=None, limit=None,
           conditions=None) -> list[dict]:
    """Filter shelves for pilots and partial runs. `replicates` is a count: keep r0..r{n-1}."""
    out = []
    for s in shelves:
        if conditions and s["condition"] not in conditions:
            continue
        if categories and s["category"] not in categories:
            continue
        if replicates is not None and int(s["base_id"].rsplit("-r", 1)[1]) >= replicates:
            continue
        if variants and s["variant"] not in variants:
            continue
        out.append(s)
    return out[:limit] if limit else out


def load_env() -> None:
    """Load keys from .env without ever printing them."""
    from dotenv import load_dotenv

    from study.config import ROOT

    load_dotenv(ROOT / ".env", override=False)


def reuse_index(records: list[dict]) -> dict:
    """(content_hash, sample, mode) -> an earlier record with exactly that input, from any run."""
    idx = {}
    for r in records:
        if r.get("content_hash") and r.get("valid", True):
            idx.setdefault((r["content_hash"], r.get("sample", 0), r.get("mode", "choice")), r)
    return idx


def reused(record: dict, key: str, tag: str, shelf_id: str) -> dict:
    return {**record, "key": key, "tag": tag, "shelf_id": shelf_id, "reused_from": record["key"]}
