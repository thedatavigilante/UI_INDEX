#!/usr/bin/env python3
"""
Fetch HUD Fair Market Rents (FMR) for DMV metro areas.

Updates Weekly_Housing column in data/dmv_macro_baselines.csv.
Weekly housing cost = 2-bedroom FMR / 4.33 (weeks per month).

Source: HUD User FMR API — https://www.huduser.gov/portal/dataset/fmr-api.html
Auth: Bearer token from HUD_TOKEN env var (free registration required).

Metro area mapping:
  Maryland → Baltimore-Columbia-Towson, MD MSA
  Virginia → Washington-Arlington-Alexandria, VA-MD-WV HUD Metro
  DC       → Washington-Arlington-Alexandria, DC-VA-MD-WV HUD Metro

Without HUD_TOKEN, the script prints instructions and leaves CSV unchanged.

Run: python fetch_housing.py
"""
import csv
import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

HUD_TOKEN = os.environ.get("HUD_TOKEN", "")
HUD_BASE = "https://www.huduser.gov/hudapi/public/fmr"

ROOT = Path(__file__).parent
CSV_PATH = ROOT / "data" / "dmv_macro_baselines.csv"

# HUD metro entity IDs for target areas (FY2024 identifiers)
# Find via: GET /hudapi/public/fmr/listMetroAreas
HUD_METRO_MAP = {
    "Maryland": {
        "entityid": "METRO12580M12580",   # Baltimore-Columbia-Towson, MD MSA
        "label": "Baltimore-Columbia-Towson, MD MSA",
    },
    "Virginia": {
        "entityid": "METRO47900M47900",   # Washington-Arlington-Alexandria, VA-MD-WV
        "label": "Washington-Arlington-Alexandria, VA-MD-WV HUD Metro FMR Area",
    },
    "District of Columbia": {
        "entityid": "METRO47900M47900",   # Same metro, DC portion
        "label": "Washington-Arlington-Alexandria, DC-VA-MD-WV HUD Metro FMR Area",
    },
}

WEEKS_PER_MONTH = 4.33


def _fetch_hud(path: str) -> dict | None:
    """GET a HUD API endpoint with Bearer token. 3-attempt retry with exponential backoff."""
    url = f"{HUD_BASE}/{path.lstrip('/')}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {HUD_TOKEN}",
            "User-Agent": "UI-Index-HUD-Fetcher/1.0",
        },
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:200]
            print(f"  HUD HTTP {e.code} (attempt {attempt + 1}/3): {body}")
            if e.code in (401, 403, 404):
                return None  # Auth/not-found errors won't improve on retry
        except Exception as e:
            print(f"  HUD fetch error (attempt {attempt + 1}/3): {e}")
        if attempt < 2:
            time.sleep(2 ** (attempt + 1))
    return None


def get_fmr_for_metro(entityid: str, year: int = None) -> dict | None:
    """
    Fetch FMR data for a metro area.
    Returns dict with fmr_0br..fmr_4br or None.
    """
    path = f"data/{entityid}"
    if year:
        path += f"/{year}"
    return _fetch_hud(path)


def fmr_to_weekly(fmr_monthly: float) -> int:
    """Convert monthly FMR to weekly cost, rounded to nearest dollar."""
    return round(fmr_monthly / WEEKS_PER_MONTH)


def load_existing_csv() -> list[dict]:
    if not CSV_PATH.exists():
        return []
    with open(CSV_PATH, "r", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(rows: list[dict], fieldnames: list[str]):
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 60)
    print("HUD FAIR MARKET RENT FETCHER")
    print("=" * 60)

    if not HUD_TOKEN:
        print("\n⚠️  HUD_TOKEN not set.")
        print("   Register for a free token at: https://www.huduser.gov/portal/dataset/fmr-api.html")
        print("   Then add HUD_TOKEN=your_token to your .env file.")
        print("\n   Weekly_Housing values in dmv_macro_baselines.csv remain unchanged.")
        return

    rows = load_existing_csv()
    if not rows:
        print("ERROR: Could not load existing CSV")
        return

    # Detect fieldnames from existing CSV (preserve all columns)
    fieldnames = list(rows[0].keys())
    for extra in ["_housing_source", "_fetched_at"]:
        if extra not in fieldnames:
            fieldnames.append(extra)

    print(f"\nFetching FMR data for {len(HUD_METRO_MAP)} jurisdictions...")
    updated_count = 0

    for row in rows:
        jurisdiction = row.get("Jurisdiction", "")
        if jurisdiction not in HUD_METRO_MAP:
            continue

        meta = HUD_METRO_MAP[jurisdiction]
        print(f"\n  {jurisdiction} — {meta['label']}")

        fmr_data = get_fmr_for_metro(meta["entityid"])
        if not fmr_data:
            print(f"    HUD fetch failed — keeping existing: ${row.get('Weekly_Housing', 'N/A')}")
            continue

        # FMR response structure: {"data": {"basicdata": {"fmr_2br": ...}}}
        basic = (fmr_data.get("data") or {}).get("basicdata") or fmr_data.get("basicdata") or fmr_data
        fmr_2br = basic.get("fmr_2") or basic.get("fmr_2br")

        if fmr_2br is None:
            print(f"    No 2-bedroom FMR found in response. Keys: {list(basic.keys())[:8]}")
            print(f"    Keeping existing: ${row.get('Weekly_Housing', 'N/A')}")
            continue

        weekly = fmr_to_weekly(float(fmr_2br))
        old = row.get("Weekly_Housing", "N/A")
        row["Weekly_Housing"] = weekly
        row["_housing_source"] = f"HUD FMR 2BR {meta['entityid']} ÷ 4.33"
        row["_fetched_at"] = datetime.now().isoformat()
        print(f"    FMR 2BR: ${float(fmr_2br):,.0f}/mo → ${weekly}/wk  (was: {old})")
        updated_count += 1
        time.sleep(0.3)

    write_csv(rows, fieldnames)
    print(f"\n✅ Updated {updated_count} rows in {CSV_PATH}")


if __name__ == "__main__":
    main()
