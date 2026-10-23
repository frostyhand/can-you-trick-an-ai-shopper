from collections import Counter

import pytest

from study.catalog import CATALOG, close_briefs
from study.config import REPLICATES, TRICKS
from study.generate import VARIANTS, build_shelves

# Fields each trick is allowed to touch on the target listing.
ALLOWED = {
    "anchor": {"was_price", "discount"},
    "scarcity": {"availability"},
    "urgency": {"deal"},
    "badge": {"badge"},
    "charm": {"price"},
    "injection_overt": {"description"},
    "injection_subtle": {"description"},
    "social_proof": {"review_count"},
    "sponsored": {"label"},
    "thin_page": {"rating", "review_count", "specs", "description"},
}


@pytest.fixture(scope="module")
def shelves():
    return build_shelves()


@pytest.fixture(scope="module")
def by_base(shelves):
    out = {}
    for s in shelves:
        out.setdefault(s["base_id"], {})[s["variant"]] = s
    return out


def test_counts(shelves, by_base):
    n_base = sum(len(c["briefs"]) for c in CATALOG.values()) * REPLICATES["clear"]
    n_base += sum(len(close_briefs(c)) for c in CATALOG.values()) * REPLICATES["close"]
    assert len(by_base) == n_base
    assert len(shelves) == n_base * len(VARIANTS)
    assert all(set(v) == set(VARIANTS) for v in by_base.values())


def test_deterministic():
    assert build_shelves() == build_shelves()


def test_ids_unique_and_slots_consistent(shelves):
    for s in shelves:
        ids = [p["id"] for p in s["products"]]
        assert len(ids) == len(set(ids))
        assert [s["meta"][i]["slot"] for i in ids] == list(range(len(ids)))


def test_target_never_over_budget(shelves):
    for s in shelves:
        assert not s["meta"][s["target_id"]]["over_budget"]
        over = [i for i, m in s["meta"].items() if m["over_budget"] and not m["is_decoy"]]
        assert len(over) == (1 if s["condition"] == "clear" else 0)


def test_close_call_products_are_interchangeable(shelves):
    for s in shelves:
        if s["condition"] != "close" or s["variant"] != "control":
            continue
        first = s["products"][0]
        for prod in s["products"]:
            assert (prod["specs"], prod["price"], prod["rating"]) == (first["specs"], first["price"], first["rating"])
        assert len({prod["review_count"] for prod in s["products"]}) == len(s["products"])


@pytest.mark.parametrize("trick", [t for t in TRICKS if t != "decoy"])
def test_trick_changes_only_target_allowed_fields(by_base, trick):
    for variants in by_base.values():
        control, treated = variants["control"], variants[trick]
        assert [p["id"] for p in control["products"]] == [p["id"] for p in treated["products"]]
        for c, t in zip(control["products"], treated["products"]):
            if c["id"] != control["target_id"]:
                assert c == t
                continue
            changed = {k for k in set(c) | set(t) if c.get(k) != t.get(k)}
            assert changed, f"{trick} changed nothing"
            assert changed <= ALLOWED[trick]


def test_decoy_pair(by_base):
    for variants in by_base.values():
        control, dc, d = variants["control"], variants["decoy_control"], variants["decoy"]
        decoy_ids = [i for i, m in d["meta"].items() if m["is_decoy"]]
        assert len(decoy_ids) == 1
        # Both decoy shelves are the control shelf plus one product in the same slot.
        for shelf in (dc, d):
            rest = [p for p in shelf["products"] if not shelf["meta"][p["id"]]["is_decoy"]]
            assert rest == control["products"]
        assert dc["meta"][decoy_ids[0]]["slot"] == d["meta"][decoy_ids[0]]["slot"]
        assert d["decoy_source_id"] == d["target_id"]
        assert dc["decoy_source_id"] != dc["target_id"]


def test_decoy_is_dominated(by_base):
    for variants in by_base.values():
        d = variants["decoy"]
        decoy = next(p for p in d["products"] if d["meta"][p["id"]]["is_decoy"])
        source = next(p for p in d["products"] if p["id"] == d["decoy_source_id"])
        price = lambda p: float(p["price"].lstrip("$").replace(",", ""))
        assert price(decoy) > price(source)
        assert decoy["rating"] < source["rating"]
        assert decoy["review_count"] < source["review_count"]
        assert decoy["specs"] == source["specs"]


def test_targets_balanced_within_category(by_base):
    per_cat = {}
    for variants in by_base.values():
        c = variants["control"]
        per_cat.setdefault((c["condition"], c["category"]), Counter())[c["meta"][c["target_id"]]["catalog_index"]] += 1
    for (condition, _), counts in per_cat.items():
        assert len(counts) == (5 if condition == "clear" else 6)
        assert max(counts.values()) - min(counts.values()) <= 1
