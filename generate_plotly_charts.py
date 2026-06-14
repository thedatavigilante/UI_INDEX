#!/usr/bin/env python3
"""
Generate interactive Plotly versions of all core figures.

Outputs self-contained HTML files to interactive/ directory.
Each file can be embedded in HTML pages via <iframe> or opened standalone.

Run: python generate_plotly_charts.py
"""
import csv
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "interactive"
OUT_DIR.mkdir(exist_ok=True)

# Brand palette
BG      = "#121212"
BG2     = "#1e1e1e"
FG      = "#e8e8e8"
MUTED   = "#888888"
GREEN   = "#00FF41"
LIME    = "#BFFF00"
GOLD    = "#D4AF37"
CRIMSON = "#DC143C"
BLUE    = "#4aa8d8"
ORANGE  = "#F39C12"
GRID    = "#2a2a2a"

STATE_COLORS = {
    "Maryland":             BLUE,
    "Virginia":             GREEN,
    "District of Columbia": GOLD,
}

LAYOUT_BASE = dict(
    paper_bgcolor=BG, plot_bgcolor=BG2,
    font=dict(color=FG, family="monospace"),
    xaxis=dict(gridcolor=GRID, linecolor=GRID, tickcolor=MUTED),
    yaxis=dict(gridcolor=GRID, linecolor=GRID, tickcolor=MUTED),
    legend=dict(bgcolor=BG2, bordercolor=GRID),
    margin=dict(l=60, r=40, t=80, b=60),
)


def _save(fig: go.Figure, name: str, title: str):
    fig.update_layout(title=dict(text=title, font=dict(color=LIME, size=16, family="monospace")))
    path = OUT_DIR / f"{name}.html"
    fig.write_html(str(path), include_plotlyjs="cdn", full_html=True)
    print(f"  ✅ {path.name}")


def load_csv() -> pd.DataFrame:
    path = DATA_DIR / "dmv_macro_baselines.csv"
    df = pd.read_csv(path)
    df["BAI"]         = df["Max_WBA"] / df["Weekly_Housing"]
    df["WBI"]         = df["Taxable_Wage_Base"] / df["Avg_Annual_Wage"]
    net               = max(0, 250 - 50)
    df["MIPI"]        = net / df["Max_WBA"]
    df["Housing_Gap"] = df["Weekly_Housing"] - df["Max_WBA"]
    return df


def fig01_bai(df: pd.DataFrame):
    fig = go.Figure()
    for jur, color in STATE_COLORS.items():
        sub = df[df["Jurisdiction"] == jur].sort_values("Year")
        fig.add_trace(go.Scatter(
            x=sub["Year"], y=sub["BAI"], name=jur,
            mode="lines+markers+text",
            line=dict(color=color, width=2.5),
            marker=dict(size=9),
            text=[f"{v:.2f}" for v in sub["BAI"]],
            textposition="top right", textfont=dict(color=color),
        ))
    fig.add_hline(y=1.0, line_dash="dash", line_color=CRIMSON,
                  annotation_text="Survival Threshold", annotation_font_color=CRIMSON)
    fig.add_hrect(y0=0.5, y1=1.0, fillcolor=CRIMSON, opacity=0.05)
    fig.update_layout(**LAYOUT_BASE, yaxis_range=[0.5, 1.6])
    fig.update_xaxes(tickvals=[2010, 2018, 2026])
    fig.update_yaxes(title_text="Benefit Adequacy Index (BAI)")
    fig.update_xaxes(title_text="Year")
    _save(fig, "fig01_bai", "BAI Decay Trajectory: 2010 → 2026")


def fig02_wbi(df: pd.DataFrame):
    fig = go.Figure()
    for jur, color in STATE_COLORS.items():
        sub = df[df["Jurisdiction"] == jur].sort_values("Year")
        fig.add_trace(go.Scatter(
            x=sub["Year"], y=sub["WBI"] * 100, name=jur,
            mode="lines+markers+text",
            line=dict(color=color, width=2.5), marker=dict(size=9, symbol="square"),
            text=[f"{v*100:.1f}%" for v in sub["WBI"]],
            textposition="top right", textfont=dict(color=color),
        ))
    fig.update_layout(**LAYOUT_BASE)
    fig.update_xaxes(tickvals=[2010, 2018, 2026], title_text="Year")
    fig.update_yaxes(title_text="Wage Base as % of Avg Annual Wage", ticksuffix="%")
    _save(fig, "fig02_wbi", "WBI Stagnation: Flat SUI Caps vs. Rising Wages")


def fig03_mipi(df: pd.DataFrame):
    fig = go.Figure()
    for jur, color in STATE_COLORS.items():
        sub = df[df["Jurisdiction"] == jur].sort_values("Year")
        fig.add_trace(go.Scatter(
            x=sub["Year"], y=sub["MIPI"], name=jur,
            mode="lines+markers+text",
            line=dict(color=color, width=2.5), marker=dict(size=9, symbol="triangle-up"),
            text=[f"{v:.2f}" for v in sub["MIPI"]],
            textposition="top right", textfont=dict(color=color),
        ))
    fig.update_layout(**LAYOUT_BASE)
    fig.update_xaxes(tickvals=[2010, 2018, 2026], title_text="Year")
    fig.update_yaxes(title_text="Multi-Income Penalty Index (MIPI)")
    _save(fig, "fig03_mipi", "MIPI Clawback Severity at $250 Side-Hustle Earnings")


def fig04_housing(df: pd.DataFrame):
    fig = make_subplots(rows=1, cols=3, subplot_titles=["Maryland", "Virginia", "DC"],
                        shared_yaxes=True)
    jurs = ["Maryland", "Virginia", "District of Columbia"]
    labels = ["Maryland", "Virginia", "DC"]
    for i, (jur, label) in enumerate(zip(jurs, labels), 1):
        sub = df[df["Jurisdiction"] == jur].sort_values("Year")
        color = STATE_COLORS[jur]
        fig.add_trace(go.Scatter(x=sub["Year"], y=sub["Weekly_Housing"], name="Housing Cost",
                                  line=dict(color=CRIMSON, width=2.5), marker=dict(size=7),
                                  showlegend=(i == 1)), row=1, col=i)
        fig.add_trace(go.Scatter(x=sub["Year"], y=sub["Max_WBA"], name="Max WBA",
                                  line=dict(color=color, width=2.5, dash="dash"), marker=dict(size=7, symbol="square"),
                                  showlegend=(i == 1)), row=1, col=i)
    fig.update_layout(**LAYOUT_BASE)
    for i in range(1, 4):
        fig.update_xaxes(tickvals=[2010, 2018, 2026], gridcolor=GRID, row=1, col=i)
        fig.update_yaxes(gridcolor=GRID, row=1, col=i)
    _save(fig, "fig04_housing", "Housing Cost vs. Maximum Weekly Benefit: The Survival Deficit")


def fig_employer_gap():
    path = DATA_DIR / "political" / "employer_contribution_gap.json"
    if not path.exists():
        print(f"  ⚠️  {path} not found — skipping employer gap charts")
        return
    with open(path) as f:
        gaps = json.load(f)

    states = [g["state"] for g in gaps]
    colors = [{"MD": BLUE, "VA": GREEN, "DC": GOLD}[s] for s in states]

    # Fig 05: per-employee gap
    fig = go.Figure(go.Bar(
        x=states,
        y=[g["per_employee_gap"] for g in gaps],
        marker_color=colors,
        text=[f"${g['per_employee_gap']:,.0f}" for g in gaps],
        textposition="outside", textfont=dict(color=FG),
    ))
    fig.update_layout(**LAYOUT_BASE)
    fig.update_yaxes(title_text="Gap ($/employee/year)", tickprefix="$")
    _save(fig, "fig05_employer_per_emp", "Per-Employee Employer Contribution Gap")

    # Fig 06: aggregate gap
    fig2 = go.Figure(go.Bar(
        x=states,
        y=[g["aggregate_gap"] / 1e6 for g in gaps],
        marker_color=colors,
        text=[f"${g['aggregate_gap']/1e6:.1f}M" for g in gaps],
        textposition="outside", textfont=dict(color=FG),
    ))
    fig2.update_layout(**LAYOUT_BASE)
    fig2.update_yaxes(title_text="Aggregate Gap ($M/year)")
    _save(fig2, "fig06_employer_aggregate", "Aggregate Employer Contribution Gap ($M/year)")


def fig_fec():
    path = DATA_DIR / "political" / "fec_funding_profiles.json"
    if not path.exists():
        print(f"  ⚠️  {path} not found — skipping FEC charts")
        return
    with open(path) as f:
        profiles = json.load(f)

    if isinstance(profiles, dict) and "data" in profiles:
        profiles = profiles["data"]

    names = [p.get("name", "Unknown")[:20] for p in profiles]
    totals = [p.get("total_receipts", 0) or 0 for p in profiles]
    biz = [p.get("business_total", 0) or 0 for p in profiles]
    labor = [p.get("labor_total", 0) or 0 for p in profiles]

    # Fig 11: total receipts
    fig = go.Figure(go.Bar(
        x=totals, y=names, orientation="h",
        marker_color=GOLD,
        text=[f"${t/1e6:.1f}M" for t in totals],
        textposition="outside", textfont=dict(color=FG),
    ))
    fig.update_layout(**LAYOUT_BASE, yaxis_autorange="reversed")
    fig.update_xaxes(title_text="Total Receipts ($)", tickprefix="$")
    _save(fig, "fig11_fec_totals", "FEC Total Campaign Receipts (2024 Cycle)")

    # Fig 12: business vs labor
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Business", x=names, y=biz, marker_color=ORANGE))
    fig2.add_trace(go.Bar(name="Labor", x=names, y=labor, marker_color=BLUE))
    fig2.update_layout(**LAYOUT_BASE, barmode="group")
    fig2.update_yaxes(title_text="Contributions ($)", tickprefix="$")
    _save(fig2, "fig12_fec_biz_labor", "Business vs Labor Contributions by Member")


def main():
    print("=" * 60)
    print("PLOTLY INTERACTIVE CHART GENERATOR")
    print(f"Output: {OUT_DIR}/")
    print("=" * 60)

    df = load_csv()
    print("\nGenerating core index figures...")
    fig01_bai(df)
    fig02_wbi(df)
    fig03_mipi(df)
    fig04_housing(df)

    print("\nGenerating employer gap figures...")
    fig_employer_gap()

    print("\nGenerating FEC figures...")
    fig_fec()

    html_files = list(OUT_DIR.glob("*.html"))
    print(f"\n✅ {len(html_files)} interactive figures in {OUT_DIR}/")


if __name__ == "__main__":
    main()
