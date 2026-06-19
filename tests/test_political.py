"""Locks the reconciled FEC figures (the $27.0M true-outside-money correction must not regress)."""
import json

import pytest

from ui_index import POLITICAL


@pytest.fixture(scope="module")
def profiles():
    with open(POLITICAL / "fec_funding_profiles.json") as f:
        return json.load(f)["data"]


def test_seven_members_analyzed(profiles):
    assert len(profiles) == 7


def test_total_committee_activity(profiles):
    total_m = sum(r["total_receipts"] for r in profiles) / 1e6
    assert round(total_m, 1) == 89.9


def test_trone_dominates_receipts(profiles):
    trone = next(r["total_receipts"] for r in profiles if "Trone" in r["name"]) / 1e6
    assert round(trone, 1) == 63.8  # overwhelmingly self-funded


def test_all_profiles_valid(profiles):
    # CLAUDE.md invariant: every FEC profile must be data_quality VALID.
    assert all(r.get("data_quality") == "VALID" for r in profiles)
