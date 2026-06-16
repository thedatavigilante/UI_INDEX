"""Provenance + asset guards: data files load, carry metadata, and figures exist."""
import csv
import json
import pytest
from src import DATA, POLITICAL, FIGURES

# Files that adhere to the {_metadata, data} provenance standard.
# (employer_contribution_gap.json is a known bare-list exception — Roadmap #30.)
METADATA_FILES = [
    "fec_funding_profiles.json",
    "fec_excluded_self_funding.json",
    "political_layer_report.json",
    "fec_quick_results.json",
]

FIGURES_EXPECTED = [
    "01_bai_decay_trajectory", "02_wbi_stagnation", "03_mipi_clawback",
    "04_housing_vs_wba_gap", "05_employer_per_employee_gap",
    "06_employer_aggregate_gap", "07_statutory_vs_expected_wage_base",
    "08_real_value_index", "11_fec_total_receipts",
    "12_fec_business_vs_labor", "13_fec_contribution_mix",
]


@pytest.mark.parametrize("fname", METADATA_FILES)
def test_json_has_metadata_block(fname):
    with open(POLITICAL / fname) as f:
        obj = json.load(f)
    assert "_metadata" in obj, f"{fname} missing _metadata provenance block"
    assert "generated_by" in obj["_metadata"]


def test_baseline_csv_loads():
    with open(DATA / "dmv_macro_baselines.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) > 0
    assert {"Jurisdiction", "Year", "Max_WBA"}.issubset(rows[0].keys())


@pytest.mark.parametrize("stem", FIGURES_EXPECTED)
def test_figure_exists(stem):
    assert (FIGURES / f"{stem}.png").exists(), f"missing figure {stem}.png"
