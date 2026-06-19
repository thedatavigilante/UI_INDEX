#!/usr/bin/env python3
"""
Fetch BLS QCEW average annual wages and CPI-U data.

Updates data/dmv_macro_baselines.csv Avg_Annual_Wage column with live BLS data.
Saves CPI annual averages to data/cpi_annual.json for use by generate_rvi_figure.py.

Sources:
  - BLS QCEW Open Data API: data.bls.gov/cew/data/api (no key required)
  - BLS Public Data API v2: api.bls.gov/publicAPI/v2 (BLS_API_KEY optional)

Run: python fetch_bls_baselines.py
"""
import csv
import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

BLS_API_KEY = os.environ.get("BLS_API_KEY", "")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

CSV_PATH = DATA_DIR / "dmv_macro_baselines.csv"
CPI_CACHE_PATH = DATA_DIR / "cpi_annual.json"

# BLS CPI-U all items series
CPI_SERIES = "CUUR0000SA0"

# BLS QCEW statewide area codes (state FIPS + "000")
AREA_CODES = {
    "Maryland":              "24000",
    "Virginia":              "51000",
    "District of Columbia":  "11000",
}

# The two historical anchor years + the most recent full QCEW year as proxy for 2026
ANCHOR_YEARS = [2010, 2018]
CURRENT_QCEW_YEAR = 2023  # Latest complete annual QCEW data

# Map CSV "Year" values to the QCEW year to fetch (2026 row uses 2023 data)
FETCH_YEAR_MAP = {2010: 2010, 2018: 2018, 2026: CURRENT_QCEW_YEAR}


def _fetch_url(url: str, retries: int = 3) -> dict | None:
    """Simple GET with exponential backoff. Returns parsed JSON or None."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "UI-Index-BLS-Fetcher/1.0 (github.com/thedatavigilante/UI_INDEX)"}
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            print(f"    HTTP {e.code} on attempt {attempt + 1}: {url}")
            if e.code in (403, 404):
                return None
        except Exception as e:
            print(f"    Error on attempt {attempt + 1}: {e}")
        if attempt < retries - 1:
            time.sleep(2 ** attempt)
    return None


def fetch_qcew_avg_annual_wage(area_code: str, year: int) -> float | None:
    """
    Fetch average annual pay from BLS QCEW Open Data API.
    URL format documented at: https://www.bls.gov/cew/downloadable-data.htm
    Returns float (dollars) or None on failure.
    """
    url = (
        f"https://data.bls.gov/cew/data/api/{year}/a/area/{area_code}"
        f"/super_sector/10/industry/10/size/0/ownership/0.json"
    )
    data = _fetch_url(url)
    if not data:
        return None
    records = data.get("data", [])
    for rec in records:
        pay = rec.get("avg_annual_pay")
        if pay:
            try:
                return float(pay)
            except (TypeError, ValueError):
                pass
    return None


def fetch_cpi_annual_averages(start_year: int, end_year: int) -> dict[int, float]:
    """
    Fetch CPI-U annual averages (period M13) via BLS Public Data API v2.
    Returns {year: cpi_value}.
    """
    payload = {
        "seriesid": [CPI_SERIES],
        "startyear": str(start_year),
        "endyear": str(end_year),
    }
    if BLS_API_KEY:
        payload["registrationkey"] = BLS_API_KEY

    encoded = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        data=encoded,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "UI-Index-BLS-Fetcher/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  CPI API error: {e}")
        return {}

    if result.get("status") != "REQUEST_SUCCEEDED":
        print(f"  CPI API returned status: {result.get('status')}")
        return {}

    cpi_map = {}
    for series in result.get("Results", {}).get("series", []):
        for obs in series.get("data", []):
            if obs.get("period") == "M13":  # M13 = annual average
                try:
                    cpi_map[int(obs["year"])] = float(obs["value"])
                except (ValueError, KeyError):
                    pass
    return cpi_map


def load_existing_csv() -> dict[tuple, dict]:
    """Load existing CSV rows keyed by (Jurisdiction, Year)."""
    rows = {}
    if CSV_PATH.exists():
        with open(CSV_PATH, "r", newline="") as f:
            for row in csv.DictReader(f):
                key = (row["Jurisdiction"], int(row["Year"]))
                rows[key] = dict(row)
    return rows


def write_csv(rows: list[dict]):
    core_fields = ["Jurisdiction", "Year", "Max_WBA", "Taxable_Wage_Base", "Avg_Annual_Wage", "Weekly_Housing"]
    fieldnames = core_fields + ["_wage_source", "_fetched_at"]
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 60)
    print("BLS BASELINE FETCHER")
    print(f"  CPI series:   {CPI_SERIES}")
    print(f"  QCEW year:    {CURRENT_QCEW_YEAR} (proxy for 2026 row)")
    if BLS_API_KEY:
        print("  BLS API key:  configured")
    else:
        print("  BLS API key:  not set (rate limit: 25 req/day — sufficient for this script)")
    print("=" * 60)

    existing = load_existing_csv()

    # ── 1. CPI-U data ────────────────────────────────────────────────────────────
    print("\n[1/2] Fetching CPI-U annual averages...")
    cpi_data = fetch_cpi_annual_averages(2005, datetime.now().year)

    if cpi_data:
        cache = {
            "series": CPI_SERIES,
            "description": "CPI-U All Items U.S. City Average — Annual Averages (M13)",
            "source": "BLS Public Data API v2",
            "fetched_at": datetime.now().isoformat(),
            "data": {str(k): v for k, v in sorted(cpi_data.items())},
        }
        with open(CPI_CACHE_PATH, "w") as f:
            json.dump(cache, f, indent=2)
        print(f"  Saved {len(cpi_data)} years of CPI data to {CPI_CACHE_PATH}")
        for yr in sorted(cpi_data):
            if yr in [2008, 2010, 2014, 2018, max(cpi_data)]:
                print(f"    {yr}: {cpi_data[yr]}")
    else:
        print("  CPI fetch failed — generate_rvi_figure.py will use hardcoded values")

    # ── 2. QCEW wages ─────────────────────────────────────────────────────────────
    print("\n[2/2] Fetching BLS QCEW average annual wages...")
    updated_rows = []

    for jurisdiction, area_code in AREA_CODES.items():
        for csv_year in [2010, 2018, 2026]:
            fetch_year = FETCH_YEAR_MAP[csv_year]
            print(f"  {jurisdiction} row {csv_year} (QCEW {fetch_year}, area {area_code})...")

            key = (jurisdiction, csv_year)
            row = dict(existing.get(key, {
                "Jurisdiction": jurisdiction,
                "Year": csv_year,
                "Max_WBA": "",
                "Taxable_Wage_Base": "",
                "Avg_Annual_Wage": "",
                "Weekly_Housing": "",
            }))

            wage = fetch_qcew_avg_annual_wage(area_code, fetch_year)
            if wage:
                old = row.get("Avg_Annual_Wage", "")
                row["Avg_Annual_Wage"] = int(round(wage, -2))  # Round to nearest $100
                row["_wage_source"] = f"BLS QCEW {fetch_year} (area {area_code})"
                print(f"    BLS: ${wage:,.0f}  (was: {old})")
            else:
                row["_wage_source"] = "manual (BLS fetch failed)"
                print(f"    BLS unavailable — keeping existing value: {row.get('Avg_Annual_Wage', 'N/A')}")

            row["_fetched_at"] = datetime.now().isoformat()
            updated_rows.append(row)
            time.sleep(0.3)

    write_csv(updated_rows)
    print(f"\n✅ Updated {CSV_PATH}")
    print("   Note: Max_WBA and Taxable_Wage_Base reflect statutory caps (from state DOL statutes).")
    print("   Note: Weekly_Housing reflects metro FMR — run fetch_housing.py to update.")


if __name__ == "__main__":
    main()
