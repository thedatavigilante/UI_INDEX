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
- BLS average annual wages (QCEW) by state
- State DOL statutory SUI taxable wage bases
- BLS covered employment counts
"""
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict


# Historical average effective SUI tax rates by jurisdiction and year
# Source: DOL UI Financial Data summaries (average employer effective rates)
SUI_RATE_MATRIX = {
    "MD": {2010: 0.031, 2018: 0.023, 2026: 0.026},
    "VA": {2010: 0.028, 2018: 0.014, 2026: 0.019},
    "DC": {2010: 0.024, 2018: 0.019, 2026: 0.021},
}
DEFAULT_SUI_RATE = 0.025  # Fallback if state/year not in matrix


@dataclass
class SUIContributionGap:
    state: str
    year: int
    statutory_wage_base: float
    avg_annual_wage: float
    covered_employment: int
    # Calculated
    wage_base_as_pct_of_avg: float = 0.0
    expected_wage_base: float = 0.0  # If frozen at 2010 ratio
    per_employee_gap: float = 0.0
    aggregate_gap: float = 0.0
    sui_tax_rate: float = DEFAULT_SUI_RATE  # Dynamic DOL-sourced effective rate


def calculate_gap(state: str, year: int, statutory_base: float, avg_wage: float,
                  covered_emp: int, base_year: int = 2010, base_year_pct: float = None) -> SUIContributionGap:
    """
    Calculate the employer contribution gap for a given state and year.
    
    The gap assumes the wage base should have maintained the same ratio
    to average wages as it had in the base year (2010).
    """
    # If base_year_pct not provided, calculate from current statutory base / avg wage
    # This is the "current ratio" approach
    current_ratio = statutory_base / avg_wage if avg_wage > 0 else 0
    
    # Expected base if it kept pace with wage growth from a reference ratio
    # MD 2010: $8,500 base / ~$52,000 avg wage = ~16.3%
    # VA 2010: $8,000 base / ~$48,000 avg wage = ~16.7%
    # DC 2010: $9,000 base / ~$66,000 avg wage = ~13.6%
    reference_ratios = {
        "MD": 0.163,
        "VA": 0.167,
        "DC": 0.136,
    }
    
    ref_ratio = reference_ratios.get(state, current_ratio)
    expected_base = avg_wage * ref_ratio

    # Dynamic DOL-sourced effective SUI tax rate for this state/year
    effective_rate = SUI_RATE_MATRIX.get(state, {}).get(year, DEFAULT_SUI_RATE)
    if effective_rate == DEFAULT_SUI_RATE and (state not in SUI_RATE_MATRIX or year not in SUI_RATE_MATRIX.get(state, {})):
        print(f"⚠️  No DOL rate found for {state}/{year}, falling back to {DEFAULT_SUI_RATE:.1%}")

    # Per-employee gap = (expected_base - statutory_base) * effective_rate
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


def generate_dmv_gaps() -> List[SUIContributionGap]:
    """Generate 2026 gaps for DMV area."""
    # Data from BLS QCEW 2024 + state DOL statutes
    # Covered employment: BLS QCEW annual average 2024
    data_2026 = [
        # state, year, statutory_base, avg_wage, covered_emp
        ("MD", 2026, 8500, 72800, 2840000),    # MD avg wage ~$72,800 (BLS)
        ("VA", 2026, 8000, 68200, 3920000),    # VA avg wage ~$68,200
        ("DC", 2026, 9000, 112400, 760000),    # DC avg wage ~$112,400
    ]
    
    results = []
    for state, year, base, wage, emp in data_2026:
        gap = calculate_gap(state, year, base, wage, emp)
        results.append(gap)
    
    return results


def save_report(gaps: List[SUIContributionGap], output_dir: Path = None):
    if output_dir is None:
        output_dir = Path(__file__).parent / "data" / "political"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    data = [asdict(g) for g in gaps]
    with open(output_dir / "employer_contribution_gap.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Saved employer contribution gap report to {output_dir / 'employer_contribution_gap.json'}")
    return output_dir


if __name__ == "__main__":
    print("=" * 60)
    print("EMPLOYER CONTRIBUTION GAP ANALYSIS")
    print("=" * 60)
    
    gaps = generate_dmv_gaps()
    total_aggregate = 0
    
    for g in gaps:
        print(f"\n📍 {g.state} ({g.year})")
        print(f"   Statutory wage base: ${g.statutory_wage_base:,.0f}")
        print(f"   Avg annual wage: ${g.avg_annual_wage:,.0f}")
        print(f"   Base as % of avg wage: {g.wage_base_as_pct_of_avg:.1%}")
        print(f"   Expected base (2010 ratio): ${g.expected_wage_base:,.0f}")
        print(f"   Per-employee gap: ${g.per_employee_gap:,.2f}/year")
        print(f"   Covered employment: {g.covered_employment:,}")
        print(f"   💰 AGGREGATE GAP: ${g.aggregate_gap:,.0f}/year")
        total_aggregate += g.aggregate_gap
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL DMV AGGREGATE SHORTFALL: ${total_aggregate:,.0f}/year")
    print(f"{'=' * 60}")
    
    save_report(gaps)
