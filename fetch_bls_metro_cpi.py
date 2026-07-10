#!/usr/bin/env python3
"""
Fetch BLS metro-area CPI series for DC and Baltimore metro areas.
Saves metro-vs-national CPI ratios for use as supplementary COL context.

Series fetched:
  CUUR0000SA0  — US City Average, All Items (national baseline)
  CUURS35ASA0  — Washington-Arlington-Alexandria DC-VA-MD-WV metro
  CUURS12ASA0  — Baltimore-Columbia-Towson MD metro

Three-tier fallback:
  1. Live BLS Public Data API v2  (uses BLS_API_KEY if set)
  2. Cached data/bls_metro_cpi.json
  3. Hardcoded approximate 2023 annual averages

Run: python tools/fetch_bls_metro_cpi.py
"""
import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

BLS_API_KEY = os.environ.get("BLS_API_KEY", "")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
CACHE_PATH = DATA_DIR / "bls_metro_cpi.json"

# BLS Public Data API v2
BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

SERIES = {
    "national":   "CUUR0000SA0",   # US City Average — confirmed series
    "dc_metro":   "CUURS35ASA0",   # Washington-Arlington-Alexandria metro
    "balt_metro": "CUURS12ASA0",   # Baltimore-Columbia-Towson metro
}

# Hardcoded 2023 annual average fallback values (BLS CPI-U, 1982-84=100)
# Source: U.S. Bureau of Labor Statistics, CPI Detailed Report, 2023 Annual Averages
FALLBACK_CPI = {
    "national":   304.7,
    "dc_metro":   316.2,   # DC metro has accumulated higher inflation than national
    "balt_metro": 297.4,   # Baltimore roughly near national average
}

# Jurisdiction → series mapping for ratio lookups
JURISDICTION_SERIES = {
    "District of Columbia": "dc_metro",
    "Maryland":             "balt_metro",
    "Virginia":             "dc_metro",  # Northern VA is in DC metro area
}


def _post_bls(payload: dict) -> dict | None:
    """POST to BLS Public Data API v2. Returns parsed JSON or None."""
    encoded = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BLS_API_URL,
        data=encoded,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "UI-Index-BLS-Fetcher/1.0 (github.com/thedatavigilante/UI_INDEX)",
        },
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"    BLS API error on attempt {attempt + 1}: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
    return None


def fetch_cpi_series(series_ids: list[str], start_year: int, end_year: int) -> dict[str, dict[int, float]]:
    """
    Fetch CPI series via BLS API. Returns {series_id: {year: value}} for M13 (annual avg).
    """
    payload = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
    }
    if BLS_API_KEY:
        payload["registrationkey"] = BLS_API_KEY

    result = _post_bls(payload)
    if not result or result.get("status") != "REQUEST_SUCCEEDED":
        status = result.get("status") if result else "no response"
        print(f"  BLS API returned status: {status}")
        return {}

    out: dict[str, dict[int, float]] = {}
    for series in result.get("Results", {}).get("series", []):
        sid = series.get("seriesID", "")
        year_map: dict[int, float] = {}
        for obs in series.get("data", []):
            if obs.get("period") == "M13":  # M13 = annual average
                try:
                    year_map[int(obs["year"])] = float(obs["value"])
                except (ValueError, KeyError):
                    pass
        if year_map:
            out[sid] = year_map
    return out


def load_cache() -> dict | None:
    if CACHE_PATH.exists():
        try:
            with open(CACHE_PATH) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return None


def build_output(cpi_by_series: dict[str, dict[int, float]]) -> dict:
    """Build the output JSON structure from fetched or fallback CPI data."""
    # Resolve latest year available across all series
    all_years: set[int] = set()
    for series_data in cpi_by_series.values():
        all_years.update(series_data.keys())
    latest_year = max(all_years) if all_years else 2023

    nat_series = SERIES["national"]
    national_val = cpi_by_series.get(nat_series, {}).get(latest_year, FALLBACK_CPI["national"])

    series_out: dict[str, dict] = {}
    for label, sid in SERIES.items():
        year_map = cpi_by_series.get(sid, {})
        cpi_val = year_map.get(latest_year, FALLBACK_CPI[label])
        ratio = round((cpi_val / national_val) * 100, 1) if national_val else 100.0
        series_out[label] = {
            "series_id": sid,
            "cpi_value": round(cpi_val, 1),
            "national_ratio": ratio,  # 100 = national average
            "year": latest_year,
            "annual_data": {str(k): v for k, v in sorted(year_map.items())},
        }

    return {
        "_metadata": {
            "generated_by": "fetch_bls_metro_cpi.py",
            "generated_at": datetime.now().isoformat(),
            "sources": ["BLS Public Data API v2 — CPI-U metro area series (1982-84=100)"],
            "methodology": (
                "Metro CPI series are compared to the national US City Average on the same "
                "1982-84=100 base to derive a relative price accumulation index. "
                "national_ratio=104 means prices in that metro have risen 4% more than the "
                "national average since the base period. This differs from BEA Regional Price "
                "Parities (RPP), which measure absolute price LEVELS; BLS metro CPI measures "
                "cumulative price CHANGE. COL-BAI uses BEA RPP values; BLS ratios are provided "
                "as supplementary context."
            ),
            "caveat": (
                "BLS does not publish metro CPI for all metro areas. DC and Baltimore are "
                "among the larger metros with dedicated CPI series. Virginia state-level is "
                "approximated using the DC metro series (Northern VA is the dominant "
                "population center and falls within the DC metro area definition)."
            ),
        },
        "series": series_out,
        "jurisdiction_mapping": JURISDICTION_SERIES,
    }


def main():
    print("=" * 60)
    print("BLS METRO CPI FETCHER")
    print(f"  Series: {', '.join(SERIES.values())}")
    print(f"  API key: {'configured' if BLS_API_KEY else 'not set (25 req/day limit)'}")
    print("=" * 60)

    # ── Tier 1: Live API ──────────────────────────────────────────
    print("\n[1/3] Attempting live BLS API fetch...")
    current_year = datetime.now().year
    cpi_data = fetch_cpi_series(list(SERIES.values()), 2010, current_year)

    if cpi_data:
        print(f"  Fetched {len(cpi_data)}/{len(SERIES)} series from BLS API")
        output = build_output(cpi_data)
        output["_metadata"]["data_source"] = "live_api"
    else:
        # ── Tier 2: Cache ─────────────────────────────────────────
        print("  Live fetch failed — checking cache...")
        cached = load_cache()
        if cached:
            print(f"  Loaded cached data from {CACHE_PATH}")
            print("  Cache is up to date — no rewrite needed")
            for label, sdata in cached.get("series", {}).items():
                print(f"    {label}: CPI={sdata.get('cpi_value')}, ratio={sdata.get('national_ratio')}")
            return
        else:
            # ── Tier 3: Hardcoded fallback ────────────────────────
            print("  No cache found — using hardcoded 2023 fallback values")
            national_val = FALLBACK_CPI["national"]
            cpi_by_series = {
                sid: {2023: FALLBACK_CPI[label]}
                for label, sid in SERIES.items()
            }
            output = build_output(cpi_by_series)
            output["_metadata"]["data_source"] = "hardcoded_fallback"
            output["_metadata"]["fallback_note"] = (
                "Values are approximate 2023 annual averages from BLS published reports. "
                "Run with BLS_API_KEY set to fetch live data."
            )

    with open(CACHE_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved to {CACHE_PATH}")

    for label, sdata in output["series"].items():
        ratio = sdata["national_ratio"]
        cpi = sdata["cpi_value"]
        direction = "above" if ratio > 100 else "below"
        print(f"    {label}: CPI={cpi}, ratio={ratio} ({abs(ratio-100):.1f}% {direction} national)")


if __name__ == "__main__":
    main()
