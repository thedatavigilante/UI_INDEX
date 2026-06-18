"""Employer Contribution Gap Calculator

Calculates the per-employee employer contribution gap caused by frozen SUI taxable wage bases.
The logic: If the SUI wage base had kept pace with average wage growth since 2010,
employers would be contributing more per worker. The gap is the difference between
what they *should* pay (inflation-adjusted base) and what they *do* pay (frozen base).

Key outputs:
  - Per-employee gap ($/worker/year)
    - Aggregate trust fund shortfall ($/state/year)
      - Percentage of underfunding

      Data sources:
        - BLS average annual wages (QCEW) by state — loaded from data/dmv_macro_baselines.csv
          - State DOL statutory SUI taxable wage bases — loaded from data/dmv_macro_baselines.csv
            - BLS covered employment counts — NOTE: covered_emp is still a static BLS estimate;
                see Roadmap item for fetch_dol_sui_rates.py to pull live figures.
                """

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

from src import DATA, POLITICAL, FIGURES  # repo-root-anchored paths


# Historical average effective SUI tax rates by jurisdiction and year
# Source: DOL UI Financial Data summaries (average employer effective rates)
SUI_RATE_MATRIX = {
        "MD": {2010: 0.031, 2018: 0.023, 2026: 0.026},
        "VA": {2010: 0.028, 2018: 0.014, 2026: 0.019},
        "DC": {2010: 0.024, 2018: 0.019, 2026: 0.021},
}
DEFAULT_SUI_RATE = 0.025  # Fallback if state/year not in matrix

# BLS QCEW covered employment 2024 annual averages by state abbreviation
# TODO: replace with live fetch via fetch_dol_sui_rates.py (Roadmap Phase 8)
# Last updated: 2026-06-12 from BLS QCEW release
COVERED_EMPLOYMENT = {
        "MD": 2_840_000,
        "VA": 3_920_000,
        "DC":   760_000,
}

# Reference 2010 wage-base ratios anchoring the gap calculation
REFERENCE_RATIOS = {
        "MD": 0.163,   # $8,500 / ~$52,000 avg wage in 2010
        "VA": 0.167,   # $8,000 / ~$48,000 avg wage in 2010
        "DC": 0.136,   # $9,000 / ~$66,000 avg wage in 2010
}


@dataclass
class SUIContributionGap:
        state: str
        year: int
        statutory_wage_base: float
        avg_annual_wage: float
        covered_employment: int
        # Calculated
        wage_base_as_pct_of_avg: float = 0.0
        expected_wage_base: float = 0.0   # If frozen at 2010 ratio
    per_employee_gap: float = 0.0
    aggregate_gap: float = 0.0
    sui_tax_rate: float = DEFAULT_SUI_RATE  # Dynamic DOL-sourced effective rate


def load_baselines_for_year(year: int) -> List[Dict]:
        """Load rows for a specific year from dmv_macro_baselines.csv.

            Returns a list of dicts with keys: Jurisdiction, Year, Max_WBA,
                Taxable_Wage_Base, Avg_Annual_Wage, Weekly_Housing.
                    """
        rows = []
        csv_path = DATA / "dmv_macro_baselines.csv"
        with open(csv_path, newline="") as f:
                    for row in csv.DictReader(f):
                                    if int(row["Year"]) == year:
                                                        rows.append(row)
                                            return rows


# State abbreviation map (CSV uses full names)
_FULL_TO_ABBR = {
        "Maryland": "MD",
        "Virginia": "VA",
        "District of Columbia": "DC",
}


def calculate_gap(
        state: str,
        year: int,
        statutory_base: float,
        avg_wage: float,
        covered_emp: int,
) -> SUIContributionGap:
        """Calculate the employer contribution gap for a given state and year."""
        current_ratio = statutory_base / avg_wage if avg_wage > 0 else 0
        ref_ratio = REFERENCE_RATIOS.get(state, current_ratio)
        expected_base = avg_wage * ref_ratio

    effective_rate = SUI_RATE_MATRIX.get(state, {}).get(year, DEFAULT_SUI_RATE)
    if effective_rate == DEFAULT_SUI_RATE and (
                state not in SUI_RATE_MATRIX or year not in SUI_RATE_MATRIX.get(state, {})
    ):
                print(f"⚠️  No DOL rate found for {state}/{year}, falling back to {DEFAULT_SUI_RATE:.1%}")

    gap = (expected_base - statutory_base) * effective_rate
    aggregate = gap * covered_emp

    return SUIContributionGap(
                state=state,
                year=year,
                statutory_wage_base=statutory_base,
                avg_annual_wage=avg_wage,
                covered_employment=covered_emp,
                wage_base_as_pct_of_avg=current_ratio,
                expected_wage_base=expected_base,
                per_employee_gap=gap,
                aggregate_gap=aggregate,
                sui_tax_rate=effective_rate,
    )


def generate_dmv_gaps(year: int = 2026) -> List[SUIContributionGap]:
        """Generate contribution gaps for DMV area using CSV baselines for the given year."""
        rows = load_baselines_for_year(year)
        if not rows:
                    raise ValueError(f"No baseline rows found for year {year} in dmv_macro_baselines.csv")

        results = []
        for row in rows:
                    abbr = _FULL_TO_ABBR.get(row["Jurisdiction"])
                    if not abbr:
                                    continue
                                covered_emp = COVERED_EMPLOYMENT.get(abbr, 0)
                    gap = calculate_gap(
                        state=abbr,
                        year=year,
                        statutory_base=float(row["Taxable_Wage_Base"]),
                        avg_wage=float(row["Avg_Annual_Wage"]),
                        covered_emp=covered_emp,
                    )
                    results.append(gap)
                return results


def save_report(gaps: List[SUIContributionGap], output_dir: Path = None):
        """Save gap results to employer_contribution_gap.json with _metadata provenance block."""
    if output_dir is None:
                output_dir = POLITICAL
            output_dir.mkdir(parents=True, exist_ok=True)

    report = {
                "_metadata": {
                                "generated_by": "src/employer_models.py",
                                "generated_at": __import__("datetime").datetime.now().isoformat(),
                                "data_sources": [
                                                    "data/dmv_macro_baselines.csv (BLS QCEW wages + DOL statutory bases)",
                                                    "COVERED_EMPLOYMENT constants (BLS QCEW 2024 annual average — static, see TODO)",
                                                    "SUI_RATE_MATRIX (DOL UI Financial Data effective rates)",
                                ],
                                "methodology": (
                                                    "Gap = (expected_wage_base - statutory_wage_base) * effective_SUI_rate. "
                                                    "Expected base = avg_annual_wage * 2010 reference ratio. "
                                                    "Per-employee gap extrapolated to aggregate via BLS covered employment."
                                ),
                                "caveat": (
                                                    "covered_employment figures are static BLS estimates (2024 release). "
                                                    "See Roadmap Phase 8 for live fetch. "
                                                    "employer_contribution_gap.json metadata wrapper added 2026-06-18 (Roadmap #30)."
                                ),
                },
                "data": [asdict(g) for g in gaps],
    }

    out_path = output_dir / "employer_contribution_gap.json"
    with open(out_path, "w") as f:
                json.dump(report, f, indent=2)
            print(f"✅ Wrote {out_path}")
    return out_path
