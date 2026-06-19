#!/usr/bin/env python3
"""
Fetch inflation data from FRED (Federal Reserve Bank of St. Louis).

Cross-validates BLS CPI-U with an independent federal source (the Fed, not BLS/OMB).
Uses regional DC-metro CPI for more locally accurate DMV purchasing-power calculations.

Series fetched:
  CPIAUCSL   — CPI-U All Items, national (mirrors BLS but served by Fed)
  CUURA311SA0 — CPI-U DC-Arlington-Alexandria metro (regional, more accurate for DMV)
  PCEPI      — PCE Price Index (Fed's preferred inflation measure, different methodology)

Saves: data/inflation_crosscheck.json

Run: python fetch_fred_inflation.py
Requires: FRED_API_KEY in .env (free at fred.stlouisfed.org/api_keys)
"""
import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_PATH = DATA_DIR / "inflation_crosscheck.json"

# Freeze years per jurisdiction (policy anchors — when benefit cap was last raised)
FREEZE_YEARS = {
    "Maryland":             2014,
    "Virginia":             2008,
    "District of Columbia": 2018,
}
CURRENT_YEAR = 2026

SERIES = {
    "CPIAUCSL":    "CPI-U All Items, U.S. City Average (BLS via FRED)",
    "CUURA311SA0": "CPI-U Washington-Arlington-Alexandria Metro Area",
    "PCEPI":       "Personal Consumption Expenditures Price Index (Fed preferred)",
}


def fetch_series(series_id: str, start: str = "2005-01-01") -> dict[int, float] | None:
    """Fetch annual average observations from FRED. Returns {year: value} or None."""
    if not FRED_API_KEY:
        return None

    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start,
        "frequency": "a",       # Annual
        "aggregation_method": "avg",
    }
    url = f"{FRED_BASE}?{urllib.parse.urlencode(params)}"

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "UI-Index/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode())
                result = {}
                for obs in data.get("observations", []):
                    if obs.get("value") not in (".", ""):
                        try:
                            yr = int(obs["date"][:4])
                            result[yr] = float(obs["value"])
                        except (ValueError, KeyError):
                            pass
                return result
        except urllib.error.HTTPError as e:
            print(f"  FRED HTTP {e.code} for {series_id} (attempt {attempt+1})")
            if e.code == 400:
                return None
        except Exception as e:
            print(f"  FRED error for {series_id} (attempt {attempt+1}): {e}")
        if attempt < 2:
            time.sleep(2 ** attempt)
    return None


def compute_ratio(data: dict[int, float], from_year: int, to_year: int) -> float | None:
    """Compute inflation ratio: value[to_year] / value[from_year]."""
    v_from = data.get(from_year)
    v_to = data.get(to_year) or data.get(max(k for k in data if k <= to_year), None)
    if v_from and v_to:
        return round(v_to / v_from, 6)
    return None


def main():
    print("=" * 60)
    print("FRED INFLATION CROSS-VALIDATOR")
    print("=" * 60)

    if not FRED_API_KEY:
        print("\n⚠️  FRED_API_KEY not set.")
        print("   Register free at: https://fred.stlouisfed.org/api_keys")
        print("   Add FRED_API_KEY=your_key to .env")
        print("\n   Saving placeholder — generate_rvi_figure.py will use BLS fallback.")
        result = {
            "_metadata": {
                "source": "FRED not configured",
                "fetched_at": datetime.now().isoformat(),
                "fallback_applied": True,
                "note": "Set FRED_API_KEY in .env to enable cross-validation. Hardcoded CPI ratios active in generate_rvi_figure.py.",
            },
            "series": {},
            "crosscheck": {},
        }
        DATA_DIR.mkdir(exist_ok=True)
        with open(OUTPUT_PATH, "w") as f:
            json.dump(result, f, indent=2)
        return

    print(f"\nFetching {len(SERIES)} inflation series from FRED...")
    series_data = {}
    for sid, desc in SERIES.items():
        print(f"  {sid}: {desc}")
        data = fetch_series(sid)
        if data:
            series_data[sid] = data
            latest = max(data)
            print(f"    {len(data)} years fetched (latest: {latest}: {data[latest]:.3f})")
        else:
            print(f"    FAILED")
        time.sleep(0.5)

    # Compute cross-check ratios per jurisdiction per series
    print("\nComputing inflation ratios by jurisdiction...")
    crosscheck = {}
    for jurisdiction, freeze_yr in FREEZE_YEARS.items():
        ratios = {}
        for sid, data in series_data.items():
            ratio = compute_ratio(data, freeze_yr, CURRENT_YEAR)
            if ratio:
                ratios[sid] = ratio
                pct = (ratio - 1) * 100
                print(f"  {jurisdiction} ({freeze_yr}→{CURRENT_YEAR}) [{sid}]: {ratio:.4f} (+{pct:.1f}%)")

        # Cross-check: compare national CPI vs DC metro CPI
        nat = ratios.get("CPIAUCSL")
        metro = ratios.get("CUURA311SA0")
        if nat and metro:
            delta_pct = round((metro - nat) / nat * 100, 2)
            crosscheck[jurisdiction] = {
                "freeze_year": freeze_yr,
                "ratios": ratios,
                "preferred_ratio": metro,  # DC metro is more accurate for DMV
                "preferred_series": "CUURA311SA0",
                "national_vs_metro_delta_pct": delta_pct,
                "flag": "REVIEW" if abs(delta_pct) > 3 else "OK",
            }
            if abs(delta_pct) > 3:
                print(f"  ⚠️  {jurisdiction}: DC metro CPI differs from national by {delta_pct:+.1f}% — review")
        else:
            crosscheck[jurisdiction] = {
                "freeze_year": freeze_yr,
                "ratios": ratios,
                "preferred_ratio": nat or (list(ratios.values())[0] if ratios else None),
                "preferred_series": "CPIAUCSL" if nat else (list(ratios.keys())[0] if ratios else None),
                "national_vs_metro_delta_pct": None,
                "flag": "PARTIAL",
            }

    result = {
        "_metadata": {
            "source": "Federal Reserve Bank of St. Louis (FRED)",
            "series_fetched": list(series_data.keys()),
            "fetched_at": datetime.now().isoformat(),
            "current_year": CURRENT_YEAR,
            "fallback_applied": len(series_data) == 0,
            "note": (
                "CUURA311SA0 (DC metro CPI) preferred over national CPI for DMV accuracy. "
                "PCEPI provides methodologically independent cross-check."
            ),
        },
        "series": {sid: {str(yr): val for yr, val in sorted(d.items())}
                   for sid, d in series_data.items()},
        "crosscheck": crosscheck,
    }

    DATA_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n✅ Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
