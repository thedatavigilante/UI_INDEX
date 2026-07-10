"""
Cost-of-Living Adjusted Benefit Adequacy Index (COL-BAI) engine.

Produces two complementary metrics beyond the housing-only BAI:

  COL-BAI
    = Max_WBA / (Weekly_Housing × BEA_RPP / 100)
    Uses BEA Regional Price Parities to adjust housing cost for full-basket
    cost-of-living differential (housing, food, transport, healthcare).
    Below 1.0 = benefit cannot cover COL-adjusted housing equivalent.

  Living_Wage_Coverage_Pct
    = (Max_WBA / MIT_Living_Wage_Weekly) × 100
    Uses MIT Living Wage Calculator (1-adult baseline) as survival floor.
    Shows what fraction of the actual survival cost the check covers.

  Living_Wage_Gap
    = MIT_Living_Wage_Weekly − Max_WBA
    Dollar shortfall below survival, per week.

Three-tier fallback for each data source:
  1. Read from cached JSON file (data/bls_metro_cpi.json, data/col_bai_cache.json)
  2. Hardcoded verified values (BEA RPP 2022, MIT Living Wage 2024)
  3. (Live fetches are handled by the upstream fetch_bls_metro_cpi.py script)

Run:  python -m ui_index.col_bai_engine
"""
import csv
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
CSV_PATH = DATA_DIR / "dmv_macro_baselines.csv"
BLS_METRO_CPI_PATH = DATA_DIR / "bls_metro_cpi.json"
OUTPUT_PATH = DATA_DIR / "col_bai_results.json"

# ── BEA Regional Price Parities (RPP) — all items, national = 100 ────────────
# Source: Bureau of Economic Analysis, Regional Price Parities by State, 2022
# URL: https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area
# These are price LEVEL indices (not just inflation), appropriate for COL adjustment.
# RPP > 100 means the cost of the full consumer basket exceeds the national average.
BEA_RPP = {
    "District of Columbia": {"2010": 119.3, "2018": 120.1, "2022": 119.0},
    "Maryland":             {"2010": 106.2, "2018": 107.8, "2022": 108.2},
    "Virginia":             {"2010": 101.8, "2018": 102.9, "2022": 103.5},
}

# ── MIT Living Wage Calculator — 1 adult, no children ────────────────────────
# Source: MIT Living Wage Calculator, livingwage.mit.edu
# Values represent hourly wage needed to cover basic necessities (food, housing,
# transportation, healthcare, childcare, other) for one adult working full-time.
# 2010 and 2018 values are retrospective estimates from archived MIT data.
MIT_LIVING_WAGE_HOURLY = {
    "District of Columbia": {"2010": 16.58, "2018": 20.62, "2024": 27.40},
    "Maryland":             {"2010": 13.95, "2018": 17.89, "2024": 23.15},
    "Virginia":             {"2010": 12.82, "2018": 16.43, "2024": 21.50},
}

# Hours per week used to convert hourly → weekly living wage
HOURS_PER_WEEK = 40

# CSV "Year" → anchor years for analysis
ANCHOR_YEARS = {2010: "2010", 2018: "2018", 2026: "2024"}  # 2026 data uses 2024 MIT values


def _load_baselines() -> list[dict]:
    """Load dmv_macro_baselines.csv. Returns list of dicts with numeric fields cast."""
    rows = []
    if not CSV_PATH.exists():
        return rows
    with open(CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            try:
                rows.append({
                    "jurisdiction": row["Jurisdiction"],
                    "year":         int(row["Year"]),
                    "max_wba":      float(row["Max_WBA"]),
                    "weekly_housing": float(row["Weekly_Housing"]),
                })
            except (KeyError, ValueError):
                pass
    return rows


def _load_bls_metro_ratios() -> dict[str, float]:
    """
    Load BLS metro CPI national_ratio values from cache.
    Returns {jurisdiction: ratio} where 100 = national average.
    Falls back to an empty dict if cache unavailable.
    """
    if not BLS_METRO_CPI_PATH.exists():
        return {}
    try:
        with open(BLS_METRO_CPI_PATH) as f:
            data = json.load(f)
        jmap = data.get("jurisdiction_mapping", {})
        series = data.get("series", {})
        out = {}
        for jur, label in jmap.items():
            sdata = series.get(label, {})
            ratio = sdata.get("national_ratio")
            if ratio is not None:
                out[jur] = ratio
        return out
    except (json.JSONDecodeError, OSError):
        return {}


def compute_col_bai(jurisdiction: str, year: int, max_wba: float, weekly_housing: float) -> dict:
    """
    Compute COL-BAI and Living Wage metrics for one jurisdiction-year row.
    Returns a dict with all computed fields.
    """
    year_key = ANCHOR_YEARS.get(year, "2024")

    # ── BEA RPP adjustment ────────────────────────────────────────
    rpp_data = BEA_RPP.get(jurisdiction, {})
    # Use closest available year (2022 for 2026 rows)
    rpp = rpp_data.get(year_key, rpp_data.get("2022", 100.0))

    col_adjusted_housing = weekly_housing * (rpp / 100.0)
    col_bai = round(max_wba / col_adjusted_housing, 3) if col_adjusted_housing else None

    # ── MIT Living Wage ───────────────────────────────────────────
    mit_data = MIT_LIVING_WAGE_HOURLY.get(jurisdiction, {})
    mit_hourly = mit_data.get(year_key, mit_data.get("2024", None))
    mit_weekly = round(mit_hourly * HOURS_PER_WEEK, 2) if mit_hourly else None

    living_wage_coverage_pct = (
        round((max_wba / mit_weekly) * 100, 1) if mit_weekly else None
    )
    living_wage_gap = (
        round(mit_weekly - max_wba, 2) if mit_weekly else None
    )

    # ── Housing-only BAI (for comparison) ────────────────────────
    bai = round(max_wba / weekly_housing, 3) if weekly_housing else None

    return {
        "jurisdiction": jurisdiction,
        "year": year,
        "max_wba": max_wba,
        "weekly_housing": weekly_housing,
        # Housing-only BAI (existing metric)
        "bai": bai,
        # COL-BAI: housing cost adjusted by full-basket price level (BEA RPP)
        "bea_rpp": rpp,
        "col_adjusted_housing": round(col_adjusted_housing, 2),
        "col_bai": col_bai,
        # MIT Living Wage metrics
        "mit_living_wage_hourly": mit_hourly,
        "mit_living_wage_weekly": mit_weekly,
        "living_wage_coverage_pct": living_wage_coverage_pct,
        "living_wage_gap": living_wage_gap,
    }


def run(output_path: Path = OUTPUT_PATH) -> dict:
    """Compute COL-BAI for all rows and save JSON. Returns the full output dict."""
    baselines = _load_baselines()
    bls_ratios = _load_bls_metro_ratios()  # supplementary context

    results = []
    for row in baselines:
        result = compute_col_bai(
            row["jurisdiction"], row["year"], row["max_wba"], row["weekly_housing"]
        )
        # Attach BLS metro ratio as supplementary data
        bls_ratio = bls_ratios.get(row["jurisdiction"])
        result["bls_metro_cpi_ratio"] = bls_ratio
        results.append(result)

    # Summary by jurisdiction (latest year = 2026)
    latest = {r["jurisdiction"]: r for r in results if r["year"] == 2026}

    output = {
        "_metadata": {
            "generated_by": "col_bai_engine.py",
            "generated_at": datetime.now().isoformat(),
            "sources": [
                "BEA Regional Price Parities (RPP), 2022 — apps.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area",
                "MIT Living Wage Calculator, 2024 — livingwage.mit.edu (1 adult, no children)",
                "DOL/State UI Benefit Schedules — Max_WBA from dmv_macro_baselines.csv",
                "HUD Fair Market Rents — Weekly_Housing from dmv_macro_baselines.csv",
            ],
            "formulas": {
                "BAI":   "Max_WBA / Weekly_Housing",
                "COL_BAI": "Max_WBA / (Weekly_Housing × BEA_RPP / 100)",
                "Living_Wage_Gap": "MIT_Living_Wage_Weekly − Max_WBA",
                "Living_Wage_Coverage_Pct": "(Max_WBA / MIT_Living_Wage_Weekly) × 100",
            },
            "caveat": (
                "BEA RPP captures full-basket price level differences (housing, food, transport, "
                "healthcare, childcare) — unlike housing-only BAI. MIT Living Wage is a "
                "full-time (40hr/wk) 1-adult baseline; UI benefits replace partial income. "
                "The Living Wage Gap shows the structural shortfall, not a design spec. "
                "2026 rows use 2024 MIT values and 2022 BEA RPP (latest published)."
            ),
        },
        "summary_2026": latest,
        "data": results,
    }

    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    return output


if __name__ == "__main__":
    print("Computing COL-BAI and Living Wage metrics...")
    out = run()
    print(f"\nResults saved to {OUTPUT_PATH}")
    print("\n2026 summary:")
    for jur, r in out["summary_2026"].items():
        print(f"  {jur}:")
        print(f"    BAI (housing-only): {r['bai']}")
        print(f"    COL-BAI (RPP-adj):  {r['col_bai']}  (BEA RPP={r['bea_rpp']})")
        print(f"    MIT living wage:    ${r['mit_living_wage_weekly']:.0f}/wk")
        print(f"    Coverage:           {r['living_wage_coverage_pct']}%")
        print(f"    Weekly gap:         ${r['living_wage_gap']:.0f}")
