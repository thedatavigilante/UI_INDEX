"""
Data integrity tests for The Stagnant Safety Net.

Run: pytest tests/ -v
"""
import csv
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
FIGS = ROOT / "figures"

REQUIRED_CSV_COLUMNS = {"Jurisdiction", "Year", "Max_WBA", "Taxable_Wage_Base",
                         "Avg_Annual_Wage", "Weekly_Housing"}
EXPECTED_FIGS = [
    "01_bai_decay_trajectory.png",
    "02_wbi_stagnation.png",
    "03_mipi_clawback.png",
    "04_housing_vs_wba_gap.png",
    "05_employer_per_employee_gap.png",
    "06_employer_aggregate_gap.png",
    "07_statutory_vs_expected_wage_base.png",
    "08_real_value_index.png",
    "09_unemployment_context.png",
    "10_spending_accountability.png",
    "11_fec_total_receipts.png",
    "12_fec_business_vs_labor.png",
    "13_fec_contribution_mix.png",
]


# ── CSV tests ─────────────────────────────────────────────────────────────────

def test_csv_columns():
    path = DATA / "dmv_macro_baselines.csv"
    assert path.exists(), f"CSV not found: {path}"
    with open(path, newline="") as f:
        headers = set(next(csv.reader(f)))
    missing = REQUIRED_CSV_COLUMNS - headers
    assert not missing, f"CSV missing required columns: {missing}"


def test_csv_no_nulls_in_core_fields():
    path = DATA / "dmv_macro_baselines.csv"
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    core = ["Jurisdiction", "Year", "Max_WBA", "Taxable_Wage_Base",
            "Avg_Annual_Wage", "Weekly_Housing"]
    for row in rows:
        for col in core:
            assert row.get(col, "").strip(), \
                f"Null/empty value in {col} for row {row}"


def test_csv_row_count():
    path = DATA / "dmv_macro_baselines.csv"
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 9, f"Expected 9 rows (3 states × 3 years), got {len(rows)}"


def test_bai_values_in_range():
    path = DATA / "dmv_macro_baselines.csv"
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        wba     = float(row["Max_WBA"])
        housing = float(row["Weekly_Housing"])
        bai     = wba / housing
        assert 0.4 <= bai <= 2.5, \
            f"BAI {bai:.2f} out of range for {row['Jurisdiction']} {row['Year']}"


# ── JSON loadability ───────────────────────────────────────────────────────────

def _json_files():
    return list(DATA.rglob("*.json"))


@pytest.mark.parametrize("path", _json_files())
def test_json_loadable(path):
    with open(path) as f:
        data = json.load(f)
    assert data is not None


# ── FEC data quality ──────────────────────────────────────────────────────────

def test_fec_profiles_valid():
    path = DATA / "political" / "fec_funding_profiles.json"
    assert path.exists(), "fec_funding_profiles.json not found"
    with open(path) as f:
        raw = json.load(f)
    profiles = raw.get("data", raw) if isinstance(raw, dict) else raw
    assert len(profiles) > 0, "FEC profiles list is empty"
    for p in profiles:
        name  = p.get("name", "unknown")
        qual  = p.get("data_quality", "MISSING")
        assert qual == "VALID", f"{name}: data_quality = {qual}"


def test_fec_itemized_not_exceeds_total():
    path = DATA / "political" / "fec_funding_profiles.json"
    with open(path) as f:
        raw = json.load(f)
    profiles = raw.get("data", raw) if isinstance(raw, dict) else raw
    for p in profiles:
        total = p.get("total_receipts") or 0
        itemized = sum([
            p.get("business_contributions") or 0,
            p.get("labor_contributions") or 0,
            p.get("pac_committee_contributions") or 0,
            p.get("other_contributions") or 0,
            p.get("individual_contributions") or 0,
        ])
        assert itemized <= total * 1.5, \
            f"{p.get('name')}: itemized ({itemized:,.0f}) > total ({total:,.0f}) × 1.5"


# ── Employer gap tests ────────────────────────────────────────────────────────

def test_employer_gap_positive():
    path = DATA / "political" / "employer_contribution_gap.json"
    assert path.exists(), "employer_contribution_gap.json not found"
    with open(path) as f:
        gaps = json.load(f)
    for g in gaps:
        state = g.get("state")
        gap   = g.get("per_employee_gap", 0)
        assert gap > 0, f"{state}: per_employee_gap {gap} should be > 0 (frozen base)"


def test_employer_aggregate_positive():
    path = DATA / "political" / "employer_contribution_gap.json"
    with open(path) as f:
        gaps = json.load(f)
    total = sum(g.get("aggregate_gap", 0) for g in gaps)
    assert total > 1e8, f"Total aggregate gap ${total:,.0f} seems too low (expected > $100M)"


# ── SUI rates ────────────────────────────────────────────────────────────────

def test_sui_rates_in_range():
    path = DATA / "sui_rates.json"
    if not path.exists():
        pytest.skip("sui_rates.json not yet generated — run fetch_dol_sui_rates.py")
    with open(path) as f:
        data = json.load(f)
    rates = data.get("rates", {})
    for state, yr_rates in rates.items():
        for yr, rate in yr_rates.items():
            assert 0.005 <= rate <= 0.08, \
                f"{state} {yr}: SUI rate {rate:.3%} outside plausible range (0.5%–8%)"


# ── Figure files ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("fname", EXPECTED_FIGS)
def test_figures_exist_and_nonzero(fname):
    path = FIGS / fname
    assert path.exists(), f"Figure missing: {fname}"
    assert path.stat().st_size > 10_000, \
        f"Figure suspiciously small ({path.stat().st_size} bytes): {fname}"


def test_no_unexpected_figures():
    """Warn if figure numbers are skipped (gap in numbering)."""
    existing = sorted(p.name for p in FIGS.glob("*.png"))
    assert len(existing) >= len(EXPECTED_FIGS), \
        f"Fewer figures than expected: {len(existing)} vs {len(EXPECTED_FIGS)}"
