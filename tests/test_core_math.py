"""Regression locks for the forensic indices — the published numbers are receipts."""
import pytest
from src.core_engine import UIIndexEngine


@pytest.fixture(scope="module")
def indices():
    return {(r["Jurisdiction"], r["Year"]): r for r in UIIndexEngine().compute_indices()}


def test_bai_2026_matches_published(indices):
    # These are the values on the live audit + README. Drift here = a broken claim.
    assert indices[("Maryland", 2026)]["BAI"] == 0.96
    assert indices[("Virginia", 2026)]["BAI"] == 1.02
    assert indices[("District of Columbia", 2026)]["BAI"] == 0.85


def test_bai_below_one_flags_critical(indices):
    assert indices[("Maryland", 2026)]["Systemic_Status"] == "CRITICAL DECAY"
    assert indices[("Virginia", 2026)]["Systemic_Status"] == "STABLE"  # SB1056 lifted it just over 1.0


def test_mipi_clawback_formula(indices):
    # MIPI = (earnings 250 - disregard 50) / max_wba; MD max WBA = $430 -> 200/430
    assert indices[("Maryland", 2026)]["MIPI"] == round(200 / 430, 2)


def test_wbi_regression(indices):
    # Wage base as share of avg wage — all jurisdictions well under 12%.
    assert abs(indices[("Maryland", 2026)]["WBI"] - 0.1181) < 0.001
    assert indices[("District of Columbia", 2026)]["WBI"] < 0.09


@pytest.mark.parametrize("nominal,factor,real,erosion", [
    (430, 1.4067, 306, 29),   # Maryland, frozen 2014
    (378, 1.547, 244, 35),    # Virginia, frozen 2008 (worst)
    (444, 1.326, 335, 25),    # DC, frozen 2018
])
def test_real_value_index(nominal, factor, real, erosion):
    """RVI = nominal / (CPI_2026 / CPI_base). Locks the inflation-adjusted figures."""
    computed = round(nominal / factor)
    assert computed == real
    assert round((nominal - computed) / nominal * 100) == erosion
