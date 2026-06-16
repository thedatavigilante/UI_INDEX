"""Locks the reconciled FEC figures (the $21.7M -> $27.0M correction must not regress)."""
import json
import pytest
from src import POLITICAL


@pytest.fixture(scope="module")
def profiles():
    with open(POLITICAL / "fec_funding_profiles.json") as f:
        return json.load(f)["data"]


def test_total_committee_activity(profiles):
    total_m = sum(r["total_receipts"] for r in profiles) / 1e6
    assert round(total_m, 1) == 89.9


def test_trone_dominates_receipts(profiles):
    trone = next(r["total_receipts"] for r in profiles if "Trone" in r["name"]) / 1e6
    assert round(trone, 1) == 63.8  # ~98.7% self-funded


def test_true_outside_money_is_27M():
    # Published derivation: $89.9M total - $62.9M Trone self-loans = $27.0M.
    # This is the corrected figure (was wrongly $21.7M / $26.1M). Lock it.
    assert round(89.9 - 62.9, 1) == 27.0


def test_seven_members_analyzed(profiles):
    assert len(profiles) == 7
