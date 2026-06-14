#!/usr/bin/env python3
"""
Fetch county-level unemployment rates (BLS LAUS) and median income (Census ACS)
for all DMV counties.

BLS LAUS series format: LAUCN{5-digit-FIPS}0000000000003 (unemployment rate)
Census ACS: B19013_001E (median household income) by county

Saves: data/county_data.json

Run: python fetch_county_data.py
"""
import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

BLS_API_KEY = os.environ.get("BLS_API_KEY", "")
CENSUS_KEY = os.environ.get("CENSUS_API_KEY", "DEMO_KEY")

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
OUTPUT_PATH = DATA_DIR / "county_data.json"

CENSUS_BASE = "https://api.census.gov/data/2022/acs/acs5"
BLS_API = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# DMV county FIPS codes (state_fips + county_fips = 5 digits)
# Maryland FIPS: 24; Virginia: 51; DC: 11
DMV_COUNTIES = {
    # Maryland counties
    "24001": "Allegany County, MD",
    "24003": "Anne Arundel County, MD",
    "24005": "Baltimore County, MD",
    "24009": "Calvert County, MD",
    "24011": "Caroline County, MD",
    "24013": "Carroll County, MD",
    "24015": "Cecil County, MD",
    "24017": "Charles County, MD",
    "24019": "Dorchester County, MD",
    "24021": "Frederick County, MD",
    "24023": "Garrett County, MD",
    "24025": "Harford County, MD",
    "24027": "Howard County, MD",
    "24029": "Kent County, MD",
    "24031": "Montgomery County, MD",
    "24033": "Prince George's County, MD",
    "24035": "Queen Anne's County, MD",
    "24037": "St. Mary's County, MD",
    "24039": "Somerset County, MD",
    "24041": "Talbot County, MD",
    "24043": "Washington County, MD",
    "24045": "Wicomico County, MD",
    "24047": "Worcester County, MD",
    "24510": "Baltimore City, MD",
    # Virginia counties and independent cities (major)
    "51013": "Arlington County, VA",
    "51059": "Fairfax County, VA",
    "51061": "Fauquier County, VA",
    "51107": "Loudoun County, VA",
    "51153": "Prince William County, VA",
    "51177": "Spotsylvania County, VA",
    "51179": "Stafford County, VA",
    "51510": "Alexandria City, VA",
    "51600": "Fairfax City, VA",
    "51610": "Falls Church City, VA",
    "51683": "Manassas City, VA",
    "51685": "Manassas Park City, VA",
    "51087": "Henrico County, VA",
    "51041": "Chesterfield County, VA",
    "51760": "Richmond City, VA",
    "51650": "Hampton City, VA",
    "51700": "Newport News City, VA",
    "51710": "Norfolk City, VA",
    "51735": "Poquoson City, VA",
    "51740": "Portsmouth City, VA",
    "51800": "Suffolk City, VA",
    "51810": "Virginia Beach City, VA",
    "51550": "Chesapeake City, VA",
    # DC
    "11001": "District of Columbia",
}

YEARS_TO_FETCH = [2010, 2018, 2023]  # 2023 = latest full LAUS year


def fetch_census_county_income() -> dict[str, int]:
    """Fetch median household income by county for MD, VA, DC."""
    url = (
        f"{CENSUS_BASE}?get=B19013_001E,NAME"
        f"&for=county:*&in=state:11,24,51"
        f"&key={CENSUS_KEY}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "UI-Index/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"  Census county income fetch failed: {e}")
        return {}

    income = {}
    for row in data[1:]:  # skip header
        val, name, state_fips, county_fips = row[0], row[1], row[2], row[3]
        fips5 = state_fips + county_fips
        if val and val not in ("-666666666", ""):
            try:
                income[fips5] = int(val)
            except ValueError:
                pass
    return income


def fetch_bls_laus_county(fips5_list: list[str], year: int) -> dict[str, float]:
    """
    Fetch BLS LAUS annual unemployment rates for a list of county FIPS codes.
    BLS API allows up to 50 series per request.
    Returns {fips5: unemployment_rate}.
    """
    series_ids = [f"LAUCN{fips}0000000000003" for fips in fips5_list]
    fips_by_series = {f"LAUCN{fips}0000000000003": fips for fips in fips5_list}

    payload = {
        "seriesid": series_ids,
        "startyear": str(year),
        "endyear": str(year),
    }
    if BLS_API_KEY:
        payload["registrationkey"] = BLS_API_KEY

    import json as _json
    encoded = _json.dumps(payload).encode()
    req = urllib.request.Request(
        BLS_API, data=encoded,
        headers={"Content-Type": "application/json", "User-Agent": "UI-Index/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = _json.loads(resp.read().decode())
    except Exception as e:
        print(f"  BLS LAUS fetch failed for year {year}: {e}")
        return {}

    rates = {}
    for series in result.get("Results", {}).get("series", []):
        sid = series.get("seriesID", "")
        fips = fips_by_series.get(sid)
        if not fips:
            continue
        for obs in series.get("data", []):
            if obs.get("period") == "M13":  # Annual average
                try:
                    rates[fips] = float(obs["value"])
                except (ValueError, KeyError):
                    pass
    return rates


def main():
    print("=" * 60)
    print("COUNTY DATA FETCHER — BLS LAUS + Census ACS")
    print("=" * 60)

    all_fips = list(DMV_COUNTIES.keys())

    # ── Census income (single call for latest year) ───────────────────────────
    print("\n[1/2] Fetching Census ACS median household income by county...")
    income_by_fips = fetch_census_county_income()
    print(f"  {len(income_by_fips)} county income records fetched")

    # ── BLS LAUS unemployment rates by year ──────────────────────────────────
    print("\n[2/2] Fetching BLS LAUS unemployment rates...")
    unemp_by_year: dict[int, dict[str, float]] = {}

    # BLS allows 50 series per request; batch into chunks of 49
    BATCH = 49
    for year in YEARS_TO_FETCH:
        print(f"  Year {year}...")
        year_rates = {}
        for i in range(0, len(all_fips), BATCH):
            batch = all_fips[i:i + BATCH]
            rates = fetch_bls_laus_county(batch, year)
            year_rates.update(rates)
            print(f"    Batch {i//BATCH + 1}: {len(rates)}/{len(batch)} series returned")
            time.sleep(0.5)
        unemp_by_year[year] = year_rates
        print(f"  Total for {year}: {len(year_rates)} county rates")
        time.sleep(1)

    # ── Build county records ─────────────────────────────────────────────────
    counties = []
    for fips5, name in DMV_COUNTIES.items():
        state_fips = fips5[:2]
        state = {"24": "MD", "51": "VA", "11": "DC"}[state_fips]

        record = {
            "fips": fips5,
            "name": name,
            "state": state,
            "median_income": income_by_fips.get(fips5),
            "unemployment_by_year": {
                str(yr): unemp_by_year.get(yr, {}).get(fips5)
                for yr in YEARS_TO_FETCH
            },
        }
        counties.append(record)

    result = {
        "_metadata": {
            "sources": {
                "unemployment": "BLS LAUS (Local Area Unemployment Statistics)",
                "income": "Census ACS 2022 5-Year (B19013_001E)",
            },
            "years_fetched": YEARS_TO_FETCH,
            "county_count": len(counties),
            "fetched_at": datetime.now().isoformat(),
        },
        "counties": counties,
    }

    DATA_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Saved {len(counties)} counties to {OUTPUT_PATH}")

    # Summary
    for state in ["MD", "VA", "DC"]:
        sc = [c for c in counties if c["state"] == state]
        with_rates = [c for c in sc if c["unemployment_by_year"].get("2023") is not None]
        print(f"  {state}: {len(sc)} counties, {len(with_rates)} with 2023 unemployment data")


if __name__ == "__main__":
    main()
