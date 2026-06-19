#!/usr/bin/env python3
"""
Fetch federal UI program spending from USASpending.gov.

CFDA 17.225 — Unemployment Insurance (core DOL program)
CFDA 17.207 — Employment Service (Wagner-Peyser Act)

No API key required. Public data from Treasury.

Saves: data/political/federal_spending.json

Run: python fetch_usaspending.py
"""
import json
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "political" / "federal_spending.json"

BASE = "https://api.usaspending.gov/api/v2"

PROGRAMS = {
    "17.225": "Unemployment Insurance",
    "17.207": "Employment Service (Wagner-Peyser)",
}

# State FIPS for place-of-performance filters
STATE_FIPS = {
    "MD": "24",
    "VA": "51",
    "DC": "11",
}

FISCAL_YEARS = [2010, 2018, 2023]


def _post(endpoint: str, payload: dict, retries: int = 3) -> dict | None:
    url = f"{BASE}{endpoint}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "User-Agent": "UI-Index/1.0"},
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:200]
            print(f"  HTTP {e.code} (attempt {attempt+1}): {body[:100]}")
        except Exception as e:
            print(f"  Error (attempt {attempt+1}): {e}")
        if attempt < retries - 1:
            time.sleep(2 ** attempt)
    return None


def _get(endpoint: str, retries: int = 3) -> dict | None:
    url = f"{BASE}{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "UI-Index/1.0"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            print(f"  Error (attempt {attempt+1}): {e}")
        if attempt < retries - 1:
            time.sleep(2 ** attempt)
    return None


def fetch_spending_by_state_program(state_fips: str, cfda: str, fiscal_year: int) -> float | None:
    """
    Fetch total federal spending for a CFDA program in a state for a fiscal year.
    Uses /api/v2/search/spending_by_award/ with aggregation.
    Returns total obligated amount in dollars, or None.
    """
    payload = {
        "filters": {
            "time_period": [{"start_date": f"{fiscal_year-1}-10-01", "end_date": f"{fiscal_year}-09-30"}],
            "award_type_codes": ["02", "03", "04", "05"],  # Grants
            "program_numbers": [cfda],
            "place_of_performance_locations": [{"country": "USA", "state": state_fips}],
        },
        "fields": ["Award Amount"],
        "limit": 1,
        "page": 1,
    }
    # Use spending_by_category for aggregated totals
    agg_payload = {
        "filters": payload["filters"],
        "category": "cfda",
        "limit": 10,
        "page": 1,
    }
    result = _post("/search/spending_by_category/", agg_payload)
    if result and "results" in result:
        for item in result["results"]:
            if item.get("code") == cfda:
                return item.get("obligated_amount")

    # Fallback: total spending endpoint
    total_payload = {
        "filters": payload["filters"],
    }
    result2 = _post("/search/spending_by_award/", {**payload, "fields": ["Award Amount"], "limit": 100})
    if result2 and "results" in result2:
        total = sum(r.get("Award Amount") or 0 for r in result2["results"])
        return total if total > 0 else None

    return None


def fetch_dol_ui_budget(fiscal_year: int) -> dict | None:
    """Fetch DOL (agency code 016) budget for UI-related budget functions."""
    result = _get(f"/agency/016/budget_function/?fiscal_year={fiscal_year}&limit=50")
    if not result:
        return None
    ui_functions = {}
    for item in result.get("results", []):
        name = item.get("name", "").lower()
        if any(kw in name for kw in ["unemployment", "employment", "workforce", "training"]):
            ui_functions[item.get("name")] = item.get("obligated_amount")
    return ui_functions if ui_functions else None


def main():
    print("=" * 60)
    print("USASPENDING.GOV — FEDERAL UI PROGRAM SPENDING")
    print("=" * 60)

    spending: dict = {}

    for state, fips in STATE_FIPS.items():
        spending[state] = {}
        for fy in FISCAL_YEARS:
            spending[state][fy] = {}
            for cfda, prog_name in PROGRAMS.items():
                print(f"  {state} FY{fy} CFDA {cfda} ({prog_name})...")
                amount = fetch_spending_by_state_program(fips, cfda, fy)
                spending[state][fy][cfda] = {
                    "program": prog_name,
                    "obligated_amount": amount,
                }
                if amount:
                    print(f"    ${amount:,.0f}")
                else:
                    print(f"    No data returned")
                time.sleep(0.4)

    # DOL budget overview
    print("\nFetching DOL UI budget function totals...")
    dol_budgets = {}
    for fy in FISCAL_YEARS:
        print(f"  FY{fy}...")
        budget = fetch_dol_ui_budget(fy)
        dol_budgets[str(fy)] = budget
        time.sleep(0.4)

    spending_fallback = all(
        all((fy_data.get("obligated_amount") or 0) == 0 for fy_data in fy_map.values())
        for fy_map in spending.values()
    )
    result = {
        "_metadata": {
            "source": "USASpending.gov Public API v2",
            "url": "https://api.usaspending.gov/api/v2",
            "programs": PROGRAMS,
            "fiscal_years": FISCAL_YEARS,
            "fetched_at": datetime.now().isoformat(),
            "fallback_applied": spending_fallback,
            "note": (
                "CFDA 17.225 = Unemployment Insurance grants to states. "
                "Amounts are federal obligations to state UI agencies."
            ),
        },
        "spending_by_state": {
            state: {
                str(fy): fy_data
                for fy, fy_data in state_data.items()
            }
            for state, state_data in spending.items()
        },
        "dol_budget_functions": dol_budgets,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Saved to {OUTPUT_PATH}")
    print("\nSummary:")
    for state in STATE_FIPS:
        for fy in FISCAL_YEARS:
            total = sum(
                (spending[state][fy].get(cfda, {}).get("obligated_amount") or 0)
                for cfda in PROGRAMS
            )
            if total:
                print(f"  {state} FY{fy}: ${total:,.0f}")


if __name__ == "__main__":
    main()
