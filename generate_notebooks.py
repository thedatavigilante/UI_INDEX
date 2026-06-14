#!/usr/bin/env python3
"""
Build all 4 elite Jupyter notebooks into notebooks/ directory.
Run: python generate_notebooks.py
"""
import json
from pathlib import Path

NB_DIR = Path(__file__).parent / "notebooks"
NB_DIR.mkdir(exist_ok=True)


def nb(cells: list) -> dict:
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10.0"},
        },
        "cells": cells,
    }


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source, "id": "md"}


def code(source: str) -> dict:
    return {
        "cell_type": "code", "metadata": {}, "source": source,
        "execution_count": None, "outputs": [], "id": "code",
    }


def save(notebook: dict, name: str):
    path = NB_DIR / name
    with open(path, "w") as f:
        json.dump(notebook, f, indent=1)
    print(f"  ✅ {path.name}")


# ── Notebook 1: Data Pipeline Validator ──────────────────────────────────────
save(nb([
    md("# 01 — Data Pipeline Validator\n\nValidates all API connections and shows data freshness."),
    code("""\
import json, os, sys
from pathlib import Path
from datetime import datetime

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT))
print(f"Root: {ROOT}")
print(f"Data dir: {DATA}")
"""),
    md("## API Connectivity Checks"),
    code("""\
import urllib.request, urllib.error, time

def check_url(label, url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "UI-Index-NB/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            print(f"  ✅ {label}: HTTP {r.status}")
    except urllib.error.HTTPError as e:
        print(f"  ⚠️  {label}: HTTP {e.code}")
    except Exception as e:
        print(f"  ❌ {label}: {e}")
    time.sleep(0.3)

print("Checking API endpoints...")
check_url("BLS API v2",       "https://api.bls.gov/publicAPI/v2/timeseries/data/")
check_url("BLS QCEW",         "https://data.bls.gov/cew/data/api/2023/a/area/24000/super_sector/10/industry/10/size/0/ownership/0.json")
check_url("Census ACS",       "https://api.census.gov/data/2022/acs/acs5?get=NAME&for=state:24")
check_url("FEC API",          "https://api.open.fec.gov/v1/candidates/search/?api_key=DEMO_KEY&state=MD&limit=1")
check_url("USASpending",      "https://api.usaspending.gov/api/v2/references/agency/016/")
check_url("HUD FMR",          "https://www.huduser.gov/hudapi/public/fmr/statedata/MD")
check_url("Congress.gov",     "https://api.congress.gov/v3/member?api_key=DEMO_KEY&limit=1&format=json")
check_url("DOL ETA downloads","https://oui.doleta.gov/unemploy/DataDownloads.asp")
"""),
    md("## Data File Freshness"),
    code("""\
files = {
    "dmv_macro_baselines.csv": DATA / "dmv_macro_baselines.csv",
    "cpi_annual.json":         DATA / "cpi_annual.json",
    "inflation_crosscheck.json": DATA / "inflation_crosscheck.json",
    "county_data.json":        DATA / "county_data.json",
    "sui_rates.json":          DATA / "sui_rates.json",
    "fec_funding_profiles.json": DATA / "political" / "fec_funding_profiles.json",
    "federal_spending.json":   DATA / "political" / "federal_spending.json",
}

from datetime import datetime
import os

print(f"{'File':<35} {'Exists':<8} {'Last Modified'}")
print("-" * 65)
for label, path in files.items():
    exists = path.exists()
    mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M") if exists else "—"
    status = "✅" if exists else "❌"
    print(f"{status} {label:<33} {mtime}")
"""),
    md("## BLS vs FRED Inflation Cross-Check"),
    code("""\
crosscheck_path = DATA / "inflation_crosscheck.json"
if crosscheck_path.exists():
    with open(crosscheck_path) as f:
        data = json.load(f)
    print(f"Fetched: {data['_metadata'].get('fetched_at', 'unknown')}")
    for jur, info in data.get("crosscheck", {}).items():
        flag = info.get("flag", "?")
        delta = info.get("national_vs_metro_delta_pct")
        icon = "⚠️" if flag == "REVIEW" else "✅"
        print(f"  {icon} {jur}: BLS vs DC-metro delta = {f'{delta:+.2f}%' if delta else 'N/A'} [{flag}]")
else:
    print("⚠️  Run fetch_fred_inflation.py to enable cross-check")
"""),
]), "01_data_pipeline.ipynb")

# ── Notebook 2: UI Index Analysis ─────────────────────────────────────────────
save(nb([
    md("# 02 — UI Index Forensic Analysis\n\nInteractive BAI/WBI/MIPI analysis with Plotly."),
    code("""\
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT))

df = pd.read_csv(ROOT / "data" / "dmv_macro_baselines.csv")
df["BAI"]  = df["Max_WBA"] / df["Weekly_Housing"]
df["WBI"]  = df["Taxable_Wage_Base"] / df["Avg_Annual_Wage"]
df["MIPI"] = max(0, 250 - 50) / df["Max_WBA"]
df["Housing_Gap"] = df["Weekly_Housing"] - df["Max_WBA"]

COLORS = {"Maryland": "#4aa8d8", "Virginia": "#00FF41", "District of Columbia": "#D4AF37"}
LAYOUT = dict(paper_bgcolor="#121212", plot_bgcolor="#1e1e1e",
              font=dict(color="#e8e8e8", family="monospace"),
              legend=dict(bgcolor="#1e1e1e"))
print(df.to_string())
"""),
    md("## Benefit Adequacy Index (BAI) — 2010→2026"),
    code("""\
fig = go.Figure()
for jur, color in COLORS.items():
    sub = df[df["Jurisdiction"] == jur].sort_values("Year")
    fig.add_trace(go.Scatter(x=sub["Year"], y=sub["BAI"], name=jur,
                              mode="lines+markers+text",
                              line=dict(color=color, width=2.5), marker=dict(size=9),
                              text=[f"{v:.2f}" for v in sub["BAI"]],
                              textposition="top right", textfont=dict(color=color)))
fig.add_hline(y=1.0, line_dash="dash", line_color="#DC143C",
              annotation_text="Survival Threshold (1.0)")
fig.update_layout(**LAYOUT, title="BAI Decay Trajectory: 2010 → 2026",
                  xaxis=dict(tickvals=[2010, 2018, 2026]),
                  yaxis=dict(range=[0.5, 1.7], title="BAI"))
fig.show()
"""),
    md("## Sensitivity Analysis — What if wage base tracked inflation?"),
    code("""\
# Load CPI data if available
import json
cpi_path = ROOT / "data" / "cpi_annual.json"
if cpi_path.exists():
    with open(cpi_path) as f:
        cpi_cache = json.load(f)
    cpi = {int(yr): val for yr, val in cpi_cache["data"].items()}
    print("CPI data available:")
    for yr in [2010, 2014, 2018, 2023]:
        print(f"  {yr}: {cpi.get(yr, 'N/A')}")
else:
    print("CPI cache not found — run fetch_bls_baselines.py")
    cpi = {2010: 218.1, 2018: 251.1, 2023: 304.7}

# Counterfactual: what would MD benefit cap be if indexed to CPI from 2010?
md_2010_wba = 430
for yr, cpi_val in sorted(cpi.items()):
    if yr >= 2010:
        indexed_wba = md_2010_wba * (cpi_val / cpi[2010])
        print(f"  MD CPI-indexed WBA {yr}: ${indexed_wba:,.0f}")
"""),
    md("## Housing Gap Divergence"),
    code("""\
fig2 = make_subplots(rows=1, cols=3, subplot_titles=["Maryland", "Virginia", "DC"])
for i, jur in enumerate(["Maryland", "Virginia", "District of Columbia"], 1):
    sub = df[df["Jurisdiction"] == jur].sort_values("Year")
    color = COLORS[jur]
    fig2.add_trace(go.Scatter(x=sub["Year"], y=sub["Weekly_Housing"],
                               name="Housing", line=dict(color="#DC143C", width=2.5),
                               showlegend=(i==1)), row=1, col=i)
    fig2.add_trace(go.Scatter(x=sub["Year"], y=sub["Max_WBA"],
                               name="Max WBA", line=dict(color=color, width=2.5, dash="dash"),
                               showlegend=(i==1)), row=1, col=i)
fig2.update_layout(**LAYOUT, title="Housing Cost vs. Max WBA — The Survival Deficit")
fig2.show()
"""),
]), "02_ui_index_analysis.ipynb")

# ── Notebook 3: Political Layer ────────────────────────────────────────────────
save(nb([
    md("# 03 — Political Layer Analysis\n\nFEC data explorer and committee accountability."),
    code("""\
import json, pandas as pd
import plotly.graph_objects as go
from pathlib import Path

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA = ROOT / "data" / "political"

fec_path = DATA / "fec_funding_profiles.json"
if not fec_path.exists():
    print("FEC data not found. Run: python fec_integration_v251d.py")
else:
    with open(fec_path) as f:
        raw = json.load(f)
    profiles = raw["data"] if isinstance(raw, dict) and "data" in raw else raw
    fec = pd.DataFrame(profiles)
    print(f"{len(fec)} member profiles loaded")
    print(fec[["name","state","total_receipts","business_total","labor_total"]].to_string())
"""),
    md("## Business vs Labor Contributions"),
    code("""\
LAYOUT = dict(paper_bgcolor="#121212", plot_bgcolor="#1e1e1e",
              font=dict(color="#e8e8e8", family="monospace"))
if "fec" in dir():
    fig = go.Figure()
    s = fec.sort_values("business_total", ascending=False)
    fig.add_trace(go.Bar(name="Business", x=s["name"], y=s.get("business_total", []),
                          marker_color="#F39C12"))
    fig.add_trace(go.Bar(name="Labor", x=s["name"], y=s.get("labor_total", []),
                          marker_color="#4aa8d8"))
    fig.update_layout(**LAYOUT, barmode="group",
                      title="Business vs Labor Contributions (2024 Cycle)")
    fig.show()
"""),
    md("## UI Committee Members"),
    code("""\
report_path = DATA / "political_layer_report.json"
if report_path.exists():
    with open(report_path) as f:
        report = json.load(f)
    ui_members = pd.DataFrame(report.get("ui_members_detail", []))
    if not ui_members.empty:
        print(f"UI-relevant committee members: {len(ui_members)}")
        for _, m in ui_members.iterrows():
            income = m.get("constituent_median_income")
            print(f"  {m['name']} ({m['state']}, {m['chamber']}) income: ${income:,}" if income else f"  {m['name']} ({m['state']})")
"""),
    md("## Cross-tab: Committee × Employer Contributions"),
    code("""\
if "fec" in dir() and "ui_members" in dir() and not ui_members.empty:
    ui_names = set(ui_members["name"].str.lower())
    fec["on_ui_committee"] = fec["name"].str.lower().apply(lambda n: any(u in n for u in ui_names))
    print("\\nMean employer contributions:")
    print(fec.groupby("on_ui_committee")[["business_total","total_receipts"]].mean().to_string())
"""),
]), "03_political_layer.ipynb")

# ── Notebook 4: County GIS Analysis ───────────────────────────────────────────
save(nb([
    md("# 04 — County GIS Analysis\n\nCounty-level unemployment, income, and UI exposure mapping."),
    code("""\
import json, pandas as pd
import plotly.express as px
from pathlib import Path

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
county_path = ROOT / "data" / "county_data.json"

if not county_path.exists():
    print("County data not found. Run: python fetch_county_data.py")
else:
    with open(county_path) as f:
        data = json.load(f)
    rows = []
    for c in data["counties"]:
        rates = c.get("unemployment_by_year", {})
        rows.append({
            "fips": c["fips"], "name": c["name"], "state": c["state"],
            "median_income": c.get("median_income"),
            "unemp_2023": rates.get("2023"), "unemp_2018": rates.get("2018"),
            "unemp_2010": rates.get("2010"),
        })
    counties = pd.DataFrame(rows)
    print(f"{len(counties)} counties loaded")
    print(counties.groupby("state")[["unemp_2023","median_income"]].mean().round(2).to_string())
"""),
    md("## County Unemployment Choropleth (Plotly)"),
    code("""\
if "counties" in dir():
    COLORS = {"MD": "#4aa8d8", "VA": "#00FF41", "DC": "#D4AF37"}
    fig = px.choropleth(
        counties.dropna(subset=["unemp_2023"]),
        geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
        locations="fips", color="unemp_2023",
        scope="usa", fitbounds="locations",
        color_continuous_scale=[[0,"#00FF41"],[0.5,"#D4AF37"],[1.0,"#DC143C"]],
        hover_name="name",
        hover_data={"state": True, "unemp_2023": ":.1f", "median_income": ":,"},
        title="County Unemployment Rate 2023 — DMV Region",
        labels={"unemp_2023": "Unemployment %"},
    )
    fig.update_layout(paper_bgcolor="#121212", font=dict(color="#e8e8e8"))
    fig.show()
"""),
    md("## Highest Unemployment Counties"),
    code("""\
if "counties" in dir():
    top = counties.dropna(subset=["unemp_2023"]).nlargest(15, "unemp_2023")
    print("Top 15 counties by 2023 unemployment rate:")
    print(top[["name","state","unemp_2023","unemp_2018","unemp_2010","median_income"]].to_string(index=False))
"""),
    md("## Embedded Folium Map"),
    code("""\
from pathlib import Path
map_path = ROOT / "maps" / "dmv_counties.html"
if map_path.exists():
    from IPython.display import IFrame
    display(IFrame(src=str(map_path), width="100%", height=500))
else:
    print("Map not yet generated. Run: python generate_county_map.py")
"""),
]), "04_county_gis.ipynb")

print("\\n✅ All 4 notebooks written to notebooks/")
