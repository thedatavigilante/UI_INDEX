#!/usr/bin/env python3
"""
Generate interactive Folium choropleth map of DMV counties.

Layers:
  1. Choropleth: Benefit Adequacy Index (BAI) by state, applied to county shapes.
     BAI = Max WBA ÷ Weekly Housing Cost. Below 1.0 = benefits can't cover housing.
  2. Tooltip: county name, BAI, max WBA, housing cost, housing gap,
     wage replacement rate, WBI, per-employee SUI gap.

Output: maps/dmv_counties.html

Run: python generate_county_map.py
Requires: data/dmv_macro_baselines.csv
          data/political/employer_contribution_gap.json
          data/us_counties.geojson (cached) or network access
"""
import csv
import json
from pathlib import Path

try:
    import folium
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

CSV_PATH = ROOT / "data" / "dmv_macro_baselines.csv"
GAP_PATH = ROOT / "data" / "political" / "employer_contribution_gap.json"
GEOJSON_CACHE = ROOT / "data" / "us_counties.geojson"

COUNTIES_GEOJSON_URL = (
    "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
)

DMV_STATE_FIPS = {"24", "11", "51"}
FIPS_TO_STATE = {"24": "MD", "51": "VA", "11": "DC"}
DMV_CENTER = [38.9, -77.2]


def load_state_metrics() -> dict:
    """Build per-state metric dict from CSV (2026 rows) + employer gap JSON."""
    metrics: dict = {}

    with open(CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            if row["Year"] != "2026":
                continue
            jur = row["Jurisdiction"]
            state = {"Maryland": "MD", "Virginia": "VA", "District of Columbia": "DC"}[jur]
            wba = float(row["Max_WBA"])
            housing = float(row["Weekly_Housing"])
            avg_wage = float(row["Avg_Annual_Wage"])
            tax_base = float(row["Taxable_Wage_Base"])
            metrics[state] = {
                "max_wba": wba,
                "weekly_housing": housing,
                "avg_annual_wage": avg_wage,
                "taxable_wage_base": tax_base,
                "bai": round(wba / housing, 3),
                "housing_gap": round(housing - wba, 0),
                "wbi_pct": round(tax_base / avg_wage * 100, 1),
                "replacement_rate": round(wba / (avg_wage / 52) * 100, 1),
                "per_employee_gap": None,
                "aggregate_gap": None,
            }

    if GAP_PATH.exists():
        with open(GAP_PATH) as f:
            gap_data = json.load(f)
        for g in gap_data.get("data", []):
            state = g.get("state")
            if state in metrics:
                metrics[state]["per_employee_gap"] = g.get("per_employee_gap")
                metrics[state]["aggregate_gap"] = g.get("aggregate_gap")

    return metrics


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


def get_bai_color(bai: float | None) -> str:
    if bai is None:
        return "#555555"
    if bai < 0.85:
        return "#DC143C"   # crimson — severe failure
    if bai < 0.95:
        return "#E84040"   # red — significant failure
    if bai < 1.00:
        return "#F07050"   # orange-red — below threshold
    if bai < 1.10:
        return "#D4AF37"   # gold — marginal pass
    return "#00FF41"       # lime — adequate


def main():
    print("=" * 60)
    print("COUNTY MAP GENERATOR — BAI Choropleth (Folium)")
    print("=" * 60)

    if not HAS_FOLIUM:
        print("ERROR: folium not installed. Run: pip install folium")
        return

    print("\nLoading data...")
    state_metrics = load_state_metrics()
    geojson_full = load_or_fetch_geojson()

    if not geojson_full:
        print("ERROR: Could not load county GeoJSON")
        return

    dmv_geojson = filter_dmv_geojson(geojson_full)
    print(f"  DMV counties in GeoJSON: {len(dmv_geojson['features'])}")

    for state in ["MD", "VA", "DC"]:
        sm = state_metrics.get(state, {})
        bai = sm.get("bai", 0)
        gap = sm.get("housing_gap", 0)
        repl = sm.get("replacement_rate", 0)
        wbi = sm.get("wbi_pct", 0)
        per_emp = sm.get("per_employee_gap") or 0
        print(f"  {state}: BAI={bai:.3f}  housing_gap=${gap:+.0f}/wk  "
              f"replacement={repl:.1f}%  WBI={wbi:.1f}%  per_emp=${per_emp:.2f}/yr")

    # Build map
    print("\nBuilding Folium map...")
    m = folium.Map(
        location=DMV_CENTER, zoom_start=8,
        tiles="CartoDB dark_matter",
        prefer_canvas=True,
    )

    # ── BAI choropleth ────────────────────────────────────────────────────────
    bai_layer = folium.FeatureGroup(name="Benefit Adequacy Index (BAI) — 2026", show=True)

    for feature in dmv_geojson["features"]:
        fips = feature.get("id", "")
        state = FIPS_TO_STATE.get(fips[:2], "?")
        props = feature.get("properties", {})
        county_name_raw = props.get("NAME") or props.get("name") or fips
        county_name = f"{county_name_raw}, {state}"

        sm = state_metrics.get(state, {})
        bai = sm.get("bai")
        max_wba = sm.get("max_wba", 0)
        housing = sm.get("weekly_housing", 0)
        gap = sm.get("housing_gap", 0)
        replacement = sm.get("replacement_rate", 0)
        wbi = sm.get("wbi_pct", 0)
        per_emp = sm.get("per_employee_gap") or 0

        bai_color = get_bai_color(bai)
        gap_color = "#DC143C" if gap > 0 else "#00FF41"
        gap_fmt = f"+${gap:.0f}/wk shortfall" if gap > 0 else f"${abs(gap):.0f}/wk surplus"
        bai_fmt = f"{bai:.3f}" if bai is not None else "N/A"

        tooltip_html = (
            f'<div style="font-family:monospace;background:#1a1a1a;color:#e8e8e8;'
            f'padding:12px;border-radius:4px;min-width:240px;line-height:1.8">'
            f'<b style="color:#BFFF00">{county_name}</b><br>'
            f'<span style="color:#888">BAI (benefit÷housing):</span> '
            f'<b style="color:{bai_color}">{bai_fmt}</b><br>'
            f'<span style="color:#888">Max UI Benefit:</span> <b>${max_wba:.0f}/wk</b><br>'
            f'<span style="color:#888">Weekly Housing (2-BR FMR):</span> <b>${housing:.0f}/wk</b><br>'
            f'<span style="color:#888">Housing Gap:</span> '
            f'<b style="color:{gap_color}">{gap_fmt}</b><br>'
            f'<span style="color:#888">Wage Replacement Rate:</span> <b>{replacement:.1f}%</b><br>'
            f'<span style="color:#888">WBI (base÷avg wage):</span> <b>{wbi:.1f}%</b><br>'
            f'<span style="color:#888">Per-Worker UI Gap:</span> <b>${per_emp:.2f}/yr</b>'
            f'</div>'
        )

        folium.GeoJson(
            {"type": "Feature", "geometry": feature["geometry"], "properties": {}},
            style_function=lambda f, b=bai: {
                "fillColor": get_bai_color(b),
                "color": "#2a2a2a",
                "weight": 1,
                "fillOpacity": 0.75,
            },
            tooltip=folium.Tooltip(tooltip_html, sticky=False),
        ).add_to(bai_layer)

    bai_layer.add_to(m)

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_html = (
        '<div style="position:fixed;bottom:30px;left:30px;z-index:1000;'
        'background:#1a1a1a;color:#e8e8e8;padding:15px;border-radius:6px;'
        'border:1px solid #2a2a2a;font-family:monospace;font-size:12px;line-height:1.9">'
        '<b style="color:#BFFF00">Benefit Adequacy Index (BAI)</b><br>'
        '<span style="color:#aaa;font-size:10px">BAI = Max UI Benefit &divide; Weekly Housing Cost</span><br>'
        '<span style="color:#aaa;font-size:10px">Below 1.0 = benefits cannot cover housing</span><br>'
        '<br>'
        '<span style="color:#DC143C">&#9632;</span> BAI &lt; 0.85 &mdash; Severe failure<br>'
        '<span style="color:#E84040">&#9632;</span> BAI 0.85&ndash;0.95 &mdash; Significant failure<br>'
        '<span style="color:#F07050">&#9632;</span> BAI 0.95&ndash;1.00 &mdash; Below threshold<br>'
        '<span style="color:#D4AF37">&#9632;</span> BAI 1.00&ndash;1.10 &mdash; Marginal pass<br>'
        '<span style="color:#00FF41">&#9632;</span> BAI &gt; 1.10 &mdash; Adequate<br>'
        '<br>'
        '<span style="color:#DC143C">DC: 0.854</span>&nbsp;&nbsp;'
        '<span style="color:#F07050">MD: 0.956</span>&nbsp;&nbsp;'
        '<span style="color:#D4AF37">VA: 1.024</span>'
        '</div>'
    )
    m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    out = MAPS_DIR / "dmv_counties.html"
    m.save(str(out))
    print(f"\n✅ Saved to {out}")
    print(f"   Open in browser: file://{out.absolute()}")


if __name__ == "__main__":
    main()
