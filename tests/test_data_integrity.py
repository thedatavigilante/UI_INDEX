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
    "14_col_bai_comparison.png",
    "15_expense_matrix.png",
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
        # Keyword-categorized Schedule A slice only (matches validate_profile logic).
        # individual_contributions is an F3 summary field, not a categorized itemized field,
        # so it is NOT included here to avoid double-counting.
        itemized = sum([
            p.get("business_contributions") or 0,
            p.get("labor_contributions") or 0,
            p.get("pac_committee_contributions") or 0,
            p.get("other_contributions") or 0,
        ])
        assert itemized <= total * 1.1, \
            f"{p.get('name')}: itemized ({itemized:,.0f}) > total ({total:,.0f}) × 1.1"


# ── Employer gap tests ────────────────────────────────────────────────────────

def test_employer_gap_positive():
    path = DATA / "political" / "employer_contribution_gap.json"
    assert path.exists(), "employer_contribution_gap.json not found"
    with open(path) as f:
        raw = json.load(f)
    gaps = raw.get("data", raw) if isinstance(raw, dict) else raw
    for g in gaps:
        state = g.get("state")
        gap   = g.get("per_employee_gap", 0)
        assert gap > 0, f"{state}: per_employee_gap {gap} should be > 0 (frozen base)"


def test_employer_aggregate_positive():
    path = DATA / "political" / "employer_contribution_gap.json"
    with open(path) as f:
        raw = json.load(f)
    gaps = raw.get("data", raw) if isinstance(raw, dict) else raw
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


# ── COL-BAI data tests ────────────────────────────────────────────────────────

def test_col_bai_results_schema():
    path = DATA / "col_bai_results.json"
    if not path.exists():
        pytest.skip("col_bai_results.json not yet generated — run col_bai_engine.py")
    with open(path) as f:
        data = json.load(f)
    assert "_metadata" in data, "col_bai_results.json missing _metadata"
    assert "data" in data, "col_bai_results.json missing data array"
    rows = data["data"]
    assert len(rows) == 9, f"Expected 9 rows (3 states × 3 years), got {len(rows)}"
    required_fields = {"jurisdiction", "year", "bai", "col_bai", "living_wage_gap",
                       "living_wage_coverage_pct", "bea_rpp"}
    for row in rows:
        missing = required_fields - set(row.keys())
        assert not missing, \
            f"col_bai row for {row.get('jurisdiction')} {row.get('year')} missing: {missing}"


def test_col_bai_values_plausible():
    path = DATA / "col_bai_results.json"
    if not path.exists():
        pytest.skip("col_bai_results.json not yet generated — run col_bai_engine.py")
    with open(path) as f:
        data = json.load(f)
    for row in data["data"]:
        bai = row.get("bai") or 0
        col_bai = row.get("col_bai") or 0
        jur = row.get("jurisdiction")
        yr = row.get("year")
        assert 0.3 <= col_bai <= 2.5, \
            f"COL-BAI {col_bai:.3f} out of plausible range for {jur} {yr}"
        rpp = row.get("bea_rpp", 100)
        if rpp > 100:
            assert col_bai <= bai + 0.01, \
                f"{jur} {yr}: COL-BAI ({col_bai}) should be ≤ BAI ({bai}) when RPP > 100"


def test_col_bai_expense_breakdown():
    path = DATA / "col_bai_results.json"
    if not path.exists():
        pytest.skip("col_bai_results.json not yet generated — run col_bai_engine.py")
    with open(path) as f:
        data = json.load(f)
    required_cats = {"housing", "food", "transportation", "healthcare", "childcare", "other"}
    for row in data["data"]:
        jur = row.get("jurisdiction")
        yr = row.get("year")
        eb = row.get("expense_breakdown")
        assert eb is not None, f"{jur} {yr}: missing expense_breakdown"
        missing = required_cats - set(eb.keys())
        assert not missing, f"{jur} {yr}: expense_breakdown missing categories: {missing}"
        total = sum(eb.values())
        assert total > 100, f"{jur} {yr}: expense total ${total} implausibly low"


def test_bls_metro_cpi_schema():
    path = DATA / "bls_metro_cpi.json"
    if not path.exists():
        pytest.skip("bls_metro_cpi.json not yet generated — run fetch_bls_metro_cpi.py")
    with open(path) as f:
        data = json.load(f)
    assert "_metadata" in data, "bls_metro_cpi.json missing _metadata"
    assert "series" in data, "bls_metro_cpi.json missing series"
    for label in ("national", "dc_metro", "balt_metro"):
        assert label in data["series"], f"bls_metro_cpi.json missing series key: {label}"
        sdata = data["series"][label]
        ratio = sdata.get("national_ratio", 0)
        assert 70 <= ratio <= 130, f"{label}: national_ratio {ratio} outside plausible range"
