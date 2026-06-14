#!/usr/bin/env python3
"""
Generate interactive Folium choropleth map of DMV counties.

Layers:
  1. Choropleth: unemployment rate by county (red gradient)
  2. Tooltip: county name, unemployment rate, median income, state Max WBA
  3. FEC marker overlay: circle markers sized by employer contributions per district

Output: maps/dmv_counties.html

Run: python generate_county_map.py
Requires: data/county_data.json (from fetch_county_data.py)
          data/political/fec_funding_profiles.json (from fec_integration_v251d.py)
"""
import json
from pathlib import Path

try:
    import folium
    from folium.plugins import FeatureGroupSubGroup
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    import urllib.request
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

ROOT = Path(__file__).parent
MAPS_DIR = ROOT / "maps"
MAPS_DIR.mkdir(exist_ok=True)

COUNTY_DATA_PATH = ROOT / "data" / "county_data.json"
FEC_PATH = ROOT / "data" / "political" / "fec_funding_profiles.json"

# Public GeoJSON for US counties (Plotly CDN — well-maintained)
COUNTIES_GEOJSON_URL = (
    "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
)
GEOJSON_CACHE = ROOT / "data" / "us_counties.geojson"

# DMV state FIPS
DMV_STATE_FIPS = {"24", "11", "51"}

# State Max WBA (from existing CSV — these are policy caps, not fetched per county)
STATE_MAX_WBA = {"MD": 430, "VA": 430, "DC": 444}

# Map center for DMV area
DMV_CENTER = [38.9, -77.2]


def load_or_fetch_geojson() -> dict | None:
    """Load county GeoJSON from cache or download it."""
    if GEOJSON_CACHE.exists():
        with open(GEOJSON_CACHE) as f:
            return json.load(f)
    print("  Downloading county GeoJSON...")
    try:
        req = urllib.request.Request(
            COUNTIES_GEOJSON_URL, headers={"User-Agent": "UI-Index/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        with open(GEOJSON_CACHE, "w") as f:
            json.dump(data, f)
        print(f"  Saved to {GEOJSON_CACHE}")
        return data
    except Exception as e:
        print(f"  GeoJSON download failed: {e}")
        return None


def filter_dmv_geojson(geojson: dict) -> dict:
    """Keep only DMV county features."""
    dmv_features = [
        f for f in geojson.get("features", [])
        if f.get("id", "")[:2] in DMV_STATE_FIPS
    ]
    return {"type": "FeatureCollection", "features": dmv_features}


def load_county_data() -> dict[str, dict]:
    """Returns {fips5: county_record}."""
    if not COUNTY_DATA_PATH.exists():
        print(f"  ⚠️  {COUNTY_DATA_PATH} not found — run fetch_county_data.py first")
        return {}
    with open(COUNTY_DATA_PATH) as f:
        data = json.load(f)
    return {c["fips"]: c for c in data.get("counties", [])}


def load_fec_profiles() -> list[dict]:
    if not FEC_PATH.exists():
        return []
    with open(FEC_PATH) as f:
        data = json.load(f)
    return data["data"] if isinstance(data, dict) and "data" in data else data


# Approximate congressional district centroids for FEC markers (DMV)
DISTRICT_CENTROIDS = {
    "MD-01": (39.18, -75.98), "MD-02": (39.35, -76.60), "MD-03": (39.06, -76.65),
    "MD-04": (38.94, -76.83), "MD-05": (38.68, -76.70), "MD-06": (39.45, -77.40),
    "MD-07": (39.31, -76.61), "MD-08": (39.08, -77.17),
    "VA-01": (38.00, -77.40), "VA-02": (36.90, -76.20), "VA-03": (37.18, -76.95),
    "VA-04": (37.50, -77.47), "VA-05": (37.80, -78.80), "VA-06": (38.10, -79.50),
    "VA-07": (38.20, -77.65), "VA-08": (38.85, -77.10), "VA-09": (37.20, -80.40),
    "VA-10": (39.00, -77.60), "VA-11": (38.77, -77.17),
    "DC-98": (38.91, -77.01),
}


def get_unemployment_color(rate: float | None) -> str:
    if rate is None:
        return "#555555"
    if rate >= 10:  return "#DC143C"
    if rate >= 7:   return "#E84040"
    if rate >= 5:   return "#F07050"
    if rate >= 4:   return "#F0A060"
    if rate >= 3:   return "#D4AF37"
    return "#00FF41"


def main():
    print("=" * 60)
    print("COUNTY MAP GENERATOR (Folium)")
    print("=" * 60)

    if not HAS_FOLIUM:
        print("ERROR: folium not installed. Run: pip install folium")
        return

    print("\nLoading data...")
    geojson_full = load_or_fetch_geojson()
    county_data = load_county_data()
    fec_profiles = load_fec_profiles()

    if not geojson_full:
        print("ERROR: Could not load county GeoJSON")
        return

    dmv_geojson = filter_dmv_geojson(geojson_full)
    print(f"  DMV counties in GeoJSON: {len(dmv_geojson['features'])}")
    print(f"  County data records: {len(county_data)}")
    print(f"  FEC profiles: {len(fec_profiles)}")

    # Build FIPS → unemployment/income lookup
    unemp_map = {}  # fips5 → rate (latest year)
    for fips, rec in county_data.items():
        rates = rec.get("unemployment_by_year", {})
        # Use most recent available year
        for yr in ["2023", "2022", "2021", "2018"]:
            if rates.get(yr) is not None:
                unemp_map[fips] = rates[yr]
                break

    income_map = {fips: rec.get("median_income") for fips, rec in county_data.items()}

    # Build map
    print("\nBuilding Folium map...")
    m = folium.Map(
        location=DMV_CENTER, zoom_start=8,
        tiles="CartoDB dark_matter",
        prefer_canvas=True,
    )

    # ── Layer 1: Unemployment choropleth ──────────────────────────────────────
    unemp_layer = folium.FeatureGroup(name="Unemployment Rate (2023)", show=True)

    for feature in dmv_geojson["features"]:
        fips = feature.get("id", "")
        rec = county_data.get(fips, {})
        rate = unemp_map.get(fips)
        income = income_map.get(fips)
        state = {"24": "MD", "51": "VA", "11": "DC"}.get(fips[:2], "?")
        max_wba = STATE_MAX_WBA.get(state, 430)
        county_name = rec.get("name", fips)

        tooltip_html = f"""
        <div style="font-family:monospace;background:#1a1a1a;color:#e8e8e8;padding:10px;border-radius:4px;min-width:200px">
          <b style="color:#BFFF00">{county_name}</b><br>
          <span style="color:#888">Unemployment:</span> <b style="color:{get_unemployment_color(rate)}">{f'{rate:.1f}%' if rate else 'N/A'}</b><br>
          <span style="color:#888">Median Income:</span> <b>${f'{income:,}' if income else 'N/A'}</b><br>
          <span style="color:#888">State Max WBA:</span> <b>${max_wba}/wk</b><br>
          <span style="color:#888">State:</span> {state}
        </div>
        """

        folium.GeoJson(
            {"type": "Feature", "geometry": feature["geometry"], "properties": {}},
            style_function=lambda f, r=rate: {
                "fillColor": get_unemployment_color(r),
                "color": "#2a2a2a",
                "weight": 1,
                "fillOpacity": 0.7,
            },
            tooltip=folium.Tooltip(tooltip_html, sticky=False),
        ).add_to(unemp_layer)

    unemp_layer.add_to(m)

    # ── Layer 2: FEC markers ──────────────────────────────────────────────────
    fec_layer = folium.FeatureGroup(name="FEC Employer Contributions (2024)", show=True)

    for profile in fec_profiles:
        name = profile.get("name", "")
        state = profile.get("state", "")
        district = profile.get("district")
        biz_total = profile.get("business_total", 0) or 0
        total = profile.get("total_receipts", 0) or 0

        dist_key = f"{state}-{district:02d}" if district else f"{state}-98"
        coords = DISTRICT_CENTROIDS.get(dist_key)
        if not coords:
            continue

        radius = max(5, min(30, biz_total / 50000))
        popup_html = f"""
        <div style="font-family:monospace;background:#1a1a1a;color:#e8e8e8;padding:10px">
          <b style="color:#BFFF00">{name}</b><br>
          District: {dist_key}<br>
          <span style="color:#F39C12">Business:</span> ${biz_total:,.0f}<br>
          <span style="color:#4aa8d8">Total receipts:</span> ${total:,.0f}
        </div>
        """

        folium.CircleMarker(
            location=coords,
            radius=radius,
            color="#F39C12",
            fill=True,
            fill_color="#F39C12",
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{name}: ${biz_total:,.0f} employer $",
        ).add_to(fec_layer)

    fec_layer.add_to(m)

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                background:#1a1a1a;color:#e8e8e8;padding:15px;border-radius:6px;
                border:1px solid #2a2a2a;font-family:monospace;font-size:12px">
      <b style="color:#BFFF00">Unemployment Rate</b><br>
      <span style="color:#00FF41">■</span> &lt; 3%<br>
      <span style="color:#D4AF37">■</span> 3–4%<br>
      <span style="color:#F0A060">■</span> 4–5%<br>
      <span style="color:#F07050">■</span> 5–7%<br>
      <span style="color:#E84040">■</span> 7–10%<br>
      <span style="color:#DC143C">■</span> ≥ 10%<br>
      <span style="color:#555555">■</span> No data<br>
      <br>
      <span style="color:#F39C12">●</span> FEC employer $<br>
      <span style="color:#888">(circle = contribution size)</span>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    out = MAPS_DIR / "dmv_counties.html"
    m.save(str(out))
    print(f"\n✅ Saved to {out}")
    print(f"   Open in browser: file://{out.absolute()}")


if __name__ == "__main__":
    main()
