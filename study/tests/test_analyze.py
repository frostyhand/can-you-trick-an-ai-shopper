from collections import defaultdict

import pytest

from study.analyze import foolability, position_bias, rate, trick_effects
from study.generate import build_shelves


@pytest.fixture(scope="module")
def shelves():
    return build_shelves()


@pytest.fixture(scope="module")
def by_base(shelves):
    out = defaultdict(dict)
    for s in shelves:
        out[s["base_id"]][s["variant"]] = s
    return out


def fake_shares(shelves):
    """Uniform picks, except the overt injection hands the target 90%."""
    shares = {}
    for s in shelves:
        ids = [p["id"] for p in s["products"]]
        if s["variant"] == "injection_overt":
            rest = (1 - 0.9) / (len(ids) - 1)
            shares[s["shelf_id"]] = {i: (0.9 if i == s["target_id"] else rest) for i in ids}
        else:
            shares[s["shelf_id"]] = {i: 1 / len(ids) for i in ids}
    return shares


def test_trick_effects_recover_planted_effect(shelves, by_base):
    eff = trick_effects(fake_shares(shelves), by_base)
    assert eff["injection_overt"]["uplift_pp"] == pytest.approx(100 * (0.9 - 1 / 6), abs=0.01)
    assert eff["injection_overt"]["significant"]
    for trick in ("anchor", "scarcity", "badge", "decoy", "thin_page"):
        assert eff[trick]["uplift_pp"] == pytest.approx(0, abs=0.01)
        assert not eff[trick]["significant"]


def test_foolability_averages_manipulative_tricks(shelves, by_base):
    f = foolability(fake_shares(shelves), by_base)
    assert f["score_pp"] == pytest.approx(100 * (0.9 - 1 / 6) / 8, abs=0.01)


def test_position_and_rates_are_fair_under_uniform(shelves):
    shares = fake_shares(shelves)
    pos = position_bias(shares, shelves)
    assert all(v == pytest.approx(100 / 6, abs=0.01) for v in pos["slot_share_pp"])
    clear = [s for s in shelves if s["condition"] == "clear"]
    ob = rate(shares, clear, {"control"}, lambda s, pid: s["meta"][pid]["over_budget"])
    assert ob["rate_pp"] == pytest.approx(100 / 6, abs=0.01)
    dp = rate(shares, shelves, {"decoy", "decoy_control"}, lambda s, pid: s["meta"][pid]["is_decoy"])
    assert dp["rate_pp"] == pytest.approx(100 / 7, abs=0.01)
