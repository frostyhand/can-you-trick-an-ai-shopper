"""Turn a shelf into the exact inputs each model sees. Both models get the same JSON."""

import hashlib
import json

from study.config import AGENT_INSTRUCTIONS, PROMPT_VERSION


# Listing fields in the order a product page would show them.
FIELD_ORDER = [
    "id", "title", "brand", "label", "badge", "price", "was_price", "discount", "deal",
    "rating", "review_count", "availability", "specs", "description",
]


def ordered(product: dict) -> dict:
    assert set(product) <= set(FIELD_ORDER), set(product) - set(FIELD_ORDER)
    return {k: product[k] for k in FIELD_ORDER if k in product}


def state(shelf: dict) -> dict:
    return {"shopper_request": shelf["brief"], "products": [ordered(p) for p in shelf["products"]]}


def claude_user_message(shelf: dict) -> str:
    return "Here is the shopper's request and the store's products:\n\n" + json.dumps(state(shelf), indent=2)


def product_ids(shelf: dict) -> list[str]:
    return [p["id"] for p in shelf["products"]]


def content_hash(shelf: dict) -> str:
    """Fingerprint of exactly what the model sees for this shelf."""
    return hashlib.sha256(json.dumps(state(shelf), sort_keys=True).encode()).hexdigest()[:12]


def request_key(model: str, shelf: dict, sample: int = 0, tag: str = "main", mode: str = "choice") -> str:
    """Stable cache key. Changes whenever the prompt, the instructions or the shelf content change."""
    raw = f"{PROMPT_VERSION}|{tag}|{mode}|{model}|{shelf['shelf_id']}|{content_hash(shelf)}|{sample}|{AGENT_INSTRUCTIONS}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
