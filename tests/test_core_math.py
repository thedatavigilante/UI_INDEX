"""Regression locks for the forensic indices — the published numbers are receipts.

If the source CSV legitimately changes, update these assertions AND the matching
figures/HTML in the same PR. Never loosen a lock just to make CI pass.
"""
import pytest

from ui_index.core_engine import UIIndexEngine

# CPI-U anchor factors used in tools/generate_rvi_figure.py — must stay in sync.
RVI_CPI_FACTORS = {
    "Maryland": 1.4067,
    "Virginia": 1.547,
    "District of Columbia": 1.326,
}


@pytest.fixture(scope="module")
def indices():
    return {(r["Jurisdiction"], r["Year"]): r for r in UIIndexEngine().compute_indices()}


def test_bai_2026_matches_published(indices):
    # Values on the live audit + README. Drift here = a broken public claim.
    assert indices[("Maryland", 2026)]["BAI"] == 0.96
    assert indices[("Virginia", 2026)]["BAI"] == 1.02
    assert indices[("District of Columbia", 2026)]["BAI"] == 0.85


def test_systemic_status_thresholds(indices):
    assert indices[("Maryland", 2026)]["Systemic_Status"] == "CRITICAL DECAY"
    # Virginia's SB1056 wage-base lift nudged BAI just over 1.0.
    assert indices[("Virginia", 2026)]["Systemic_Status"] == "STABLE"
    assert indices[("District of Columbia", 2026)]["Systemic_Status"] == "CRITICAL DECAY"


def test_mipi_clawback_formula(indices):
    # MIPI = (earnings 250 - disregard 50) / max_wba; MD max WBA = $430 -> 200/430.
    assert indices[("Maryland", 2026)]["MIPI"] == round(200 / 430, 2)


def test_wbi_regression(indices):
    # Wage base as share of avg wage — all jurisdictions well under 12%.
    assert abs(indices[("Maryland", 2026)]["WBI"] - 0.1181) < 0.001
    assert indices[("District of Columbia", 2026)]["WBI"] < 0.09


@pytest.mark.parametrize("nominal,factor,real,erosion", [
    (430, 1.4067, 306, 29),  # Maryland, frozen 2014
    (378, 1.547,  244, 35),  # Virginia, frozen 2008 (worst)
    (444, 1.326,  335, 25),  # DC, frozen 2018
])
def test_real_value_index(nominal, factor, real, erosion):
    """RVI = nominal / (CPI_2026 / CPI_base). Locks the inflation-adjusted figures."""
    computed = round(nominal / factor)
    assert computed == real
    assert round((nominal - computed) / nominal * 100) == erosion


def test_rvi_chart_constants_consistent_with_engine(indices):
    """generate_rvi_figure.py CPI_FACTORS must yield sane real values vs engine Max_WBA."""
    for jurisdiction, factor in RVI_CPI_FACTORS.items():
        rec = indices.get((jurisdiction, 2026))
        assert rec is not None, f"Missing 2026 baseline for {jurisdiction}"
        nominal = rec["Max_WBA"]
        computed_real = round(nominal / factor)
        assert 0 < computed_real < nominal, (
            f"{jurisdiction}: RVI real value {computed_real} out of range "
            f"(nominal={nominal}, factor={factor})"
        )
