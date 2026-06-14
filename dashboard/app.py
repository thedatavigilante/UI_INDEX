"""
The Stagnant Safety Net — Interactive Dashboard
Streamlit app providing live exploration of all forensic audit data.

Run: streamlit run dashboard/app.py
"""
import json
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ── Brand palette ─────────────────────────────────────────────────────────────
BG, BG2, FG = "#121212", "#1e1e1e", "#e8e8e8"
GREEN, LIME, GOLD, CRIMSON, BLUE, ORANGE = (
    "#00FF41", "#BFFF00", "#D4AF37", "#DC143C", "#4aa8d8", "#F39C12"
)
GRID, MUTED = "#2a2a2a", "#888888"
STATE_COLORS = {"Maryland": BLUE, "Virginia": GREEN, "District of Columbia": GOLD}

LAYOUT = dict(
    paper_bgcolor=BG, plot_bgcolor=BG2,
    font=dict(color=FG, family="monospace"),
    legend=dict(bgcolor=BG2, bordercolor=GRID),
    margin=dict(l=60, r=40, t=60, b=50),
)


# ── Data loaders (cached) ──────────────────────────────────────────────────────
@st.cache_data
def load_baselines() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "dmv_macro_baselines.csv")
    df["BAI"]         = df["Max_WBA"] / df["Weekly_Housing"]
    df["WBI"]         = df["Taxable_Wage_Base"] / df["Avg_Annual_Wage"]
    df["MIPI"]        = max(0, 250 - 50) / df["Max_WBA"]
    df["Housing_Gap"] = df["Weekly_Housing"] - df["Max_WBA"]
    return df


@st.cache_data
def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


@st.cache_data
def load_county_data() -> pd.DataFrame | None:
    data = load_json(ROOT / "data" / "county_data.json")
    if not data:
        return None
    rows = []
    for c in data.get("counties", []):
        rates = c.get("unemployment_by_year", {})
        rows.append({
            "fips": c["fips"],
            "name": c["name"],
            "state": c["state"],
            "median_income": c.get("median_income"),
            "unemp_2010": rates.get("2010"),
            "unemp_2018": rates.get("2018"),
            "unemp_2023": rates.get("2023"),
        })
    return pd.DataFrame(rows)


# ── App config ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Stagnant Safety Net",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .stApp { background-color: #121212; color: #e8e8e8; }
  .stTabs [data-baseweb="tab"] { color: #888888; font-family: monospace; }
  .stTabs [aria-selected="true"] { color: #BFFF00; border-bottom-color: #BFFF00; }
  .metric-card { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 6px;
                 padding: 16px; font-family: monospace; }
  h1, h2, h3 { font-family: monospace; color: #BFFF00; }
  .stDataFrame { background: #1a1a1a; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("# THE STAGNANT SAFETY NET")
st.markdown(
    "<span style='color:#888;font-family:monospace'>"
    "Forensic audit: UI benefit erosion across DC, Maryland & Virginia — 2010→2026"
    "</span>",
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Filters")
selected_states = st.sidebar.multiselect(
    "Jurisdictions",
    ["Maryland", "Virginia", "District of Columbia"],
    default=["Maryland", "Virginia", "District of Columbia"],
)
show_year = st.sidebar.selectbox("Focus Year", [2026, 2018, 2010], index=0)
side_hustle = st.sidebar.slider("Side-Hustle Earnings ($/month)", 0, 500, 250, 25)
disregard = st.sidebar.slider("Income Disregard ($/month)", 0, 200, 50, 10)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs(["📉 Core Indices", "🗺️ County Map", "💰 FEC & Political", "🏛️ Federal Spending", "🔗 Data Sources"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1: Core Indices
# ════════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    df = load_baselines()

    # Recompute MIPI with sidebar values
    net = max(0, side_hustle - disregard)
    df["MIPI"] = net / df["Max_WBA"]

    filtered = df[df["Jurisdiction"].isin(selected_states)]

    # KPI row
    row_2026 = filtered[filtered["Year"] == show_year]
    cols = st.columns(len(row_2026))
    for col, (_, row) in zip(cols, row_2026.iterrows()):
        color = STATE_COLORS.get(row["Jurisdiction"], FG)
        bai_color = CRIMSON if row["BAI"] < 1.0 else GREEN
        col.markdown(f"""
        <div class="metric-card">
          <div style="color:{color};font-size:14px">{row['Jurisdiction']}</div>
          <div style="color:{bai_color};font-size:28px;font-weight:bold">BAI {row['BAI']:.2f}</div>
          <div style="color:#888;font-size:12px">Max WBA: ${row['Max_WBA']:,.0f}/wk</div>
          <div style="color:#888;font-size:12px">Housing: ${row['Weekly_Housing']:,.0f}/wk</div>
          <div style="color:{CRIMSON};font-size:12px">Gap: -${row['Housing_Gap']:.0f}/wk</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        # BAI chart
        fig = go.Figure()
        for jur in selected_states:
            sub = filtered[filtered["Jurisdiction"] == jur].sort_values("Year")
            fig.add_trace(go.Scatter(
                x=sub["Year"], y=sub["BAI"], name=jur,
                mode="lines+markers", line=dict(color=STATE_COLORS.get(jur, FG), width=2.5),
                marker=dict(size=9),
            ))
        fig.add_hline(y=1.0, line_dash="dash", line_color=CRIMSON,
                      annotation_text="Survival threshold")
        fig.update_layout(**LAYOUT, title="Benefit Adequacy Index (BAI)",
                          xaxis_tickvals=[2010, 2018, 2026])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Housing gap chart
        fig2 = go.Figure()
        for jur in selected_states:
            sub = filtered[filtered["Jurisdiction"] == jur].sort_values("Year")
            fig2.add_trace(go.Bar(
                x=sub["Year"], y=sub["Housing_Gap"], name=jur,
                marker_color=STATE_COLORS.get(jur, FG),
            ))
        fig2.update_layout(**LAYOUT, title="Weekly Housing Deficit ($WBA − Housing Cost)",
                           barmode="group", xaxis_tickvals=[2010, 2018, 2026])
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig3 = go.Figure()
        for jur in selected_states:
            sub = filtered[filtered["Jurisdiction"] == jur].sort_values("Year")
            fig3.add_trace(go.Scatter(
                x=sub["Year"], y=sub["WBI"] * 100, name=jur,
                mode="lines+markers", line=dict(color=STATE_COLORS.get(jur, FG), width=2.5),
                marker=dict(size=9, symbol="square"),
            ))
        fig3.update_layout(**LAYOUT, title="Wage Base Index (WBI) — SUI Cap as % of Avg Wage",
                           yaxis_ticksuffix="%", xaxis_tickvals=[2010, 2018, 2026])
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = go.Figure()
        for jur in selected_states:
            sub = filtered[filtered["Jurisdiction"] == jur].sort_values("Year")
            fig4.add_trace(go.Scatter(
                x=sub["Year"], y=sub["MIPI"], name=jur,
                mode="lines+markers", line=dict(color=STATE_COLORS.get(jur, FG), width=2.5),
                marker=dict(size=9, symbol="triangle-up"),
            ))
        fig4.update_layout(
            **LAYOUT,
            title=f"Multi-Income Penalty Index (MIPI) — ${side_hustle}/mo side hustle, ${disregard} disregard",
            xaxis_tickvals=[2010, 2018, 2026],
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("### Raw Data")
    st.dataframe(
        filtered.style.format({
            "Max_WBA": "${:,.0f}", "Taxable_Wage_Base": "${:,.0f}",
            "Avg_Annual_Wage": "${:,.0f}", "Weekly_Housing": "${:,.0f}",
            "BAI": "{:.3f}", "WBI": "{:.3f}", "MIPI": "{:.3f}", "Housing_Gap": "${:.0f}",
        }),
        use_container_width=True,
    )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2: County Map
# ════════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    map_path = ROOT / "maps" / "dmv_counties.html"
    county_df = load_county_data()

    if map_path.exists():
        with open(map_path) as f:
            map_html = f.read()
        st.components.v1.html(map_html, height=600, scrolling=False)
    else:
        st.info("County map not yet generated. Run: `python generate_county_map.py`")
        if county_df is not None:
            # Fallback: table view
            st.markdown("### County Data (table view)")
            display_cols = ["name", "state", "median_income", "unemp_2023", "unemp_2018", "unemp_2010"]
            st.dataframe(county_df[display_cols].sort_values(["state", "name"]), use_container_width=True)

    if county_df is not None:
        st.markdown("---")
        st.markdown("### County Unemployment Explorer")
        year_col = st.selectbox("Year", ["unemp_2023", "unemp_2018", "unemp_2010"],
                                format_func=lambda x: x.replace("unemp_", ""))
        state_filter = st.selectbox("State", ["All", "MD", "VA", "DC"])

        cdf = county_df.copy()
        if state_filter != "All":
            cdf = cdf[cdf["state"] == state_filter]
        cdf = cdf.dropna(subset=[year_col]).sort_values(year_col, ascending=False)

        fig_county = px.bar(
            cdf, x="name", y=year_col,
            color=year_col,
            color_continuous_scale=[[0, GREEN], [0.4, GOLD], [0.7, ORANGE], [1.0, CRIMSON]],
            title=f"Unemployment Rate by County ({year_col.replace('unemp_', '')})",
        )
        fig_county.update_layout(**LAYOUT, xaxis_tickangle=-45)
        fig_county.update_yaxes(title_text="Unemployment Rate (%)", ticksuffix="%")
        st.plotly_chart(fig_county, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3: FEC & Political Layer
# ════════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    fec_data = load_json(ROOT / "data" / "political" / "fec_funding_profiles.json")
    political_report = load_json(ROOT / "data" / "political" / "political_layer_report.json")

    if fec_data is None:
        st.info("FEC data not found. Run: `python fec_integration_v251d.py`")
    else:
        profiles = fec_data["data"] if isinstance(fec_data, dict) and "data" in fec_data else fec_data
        fec_df = pd.DataFrame(profiles)

        st.markdown("### Campaign Finance (2024 Cycle)")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Members Profiled", len(fec_df))
        if "total_receipts" in fec_df.columns:
            col_b.metric("Total Receipts", f"${fec_df['total_receipts'].sum():,.0f}")
        if "business_total" in fec_df.columns:
            col_c.metric("Total Business $", f"${fec_df['business_total'].sum():,.0f}")

        # Business vs labor chart
        if {"name", "business_total", "labor_total"}.issubset(fec_df.columns):
            fig_fec = go.Figure()
            fec_sorted = fec_df.sort_values("business_total", ascending=False)
            fig_fec.add_trace(go.Bar(name="Business", x=fec_sorted["name"],
                                      y=fec_sorted["business_total"], marker_color=ORANGE))
            fig_fec.add_trace(go.Bar(name="Labor", x=fec_sorted["name"],
                                      y=fec_sorted.get("labor_total", [0]*len(fec_sorted)),
                                      marker_color=BLUE))
            fig_fec.update_layout(**LAYOUT, barmode="group",
                                   title="Business vs Labor Contributions by Member")
            fig_fec.update_yaxes(title_text="Contributions ($)", tickprefix="$")
            st.plotly_chart(fig_fec, use_container_width=True)

        st.markdown("### Member Data Table")
        st.dataframe(fec_df, use_container_width=True)

    if political_report:
        st.markdown("---")
        st.markdown("### UI-Relevant Committee Members")
        members = political_report.get("ui_members_detail", [])
        if members:
            mdf = pd.DataFrame(members)
            display = ["name", "state", "chamber", "party", "committees", "constituent_median_income"]
            display = [c for c in display if c in mdf.columns]
            st.dataframe(mdf[display], use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4: Federal Spending
# ════════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    spending_data = load_json(ROOT / "data" / "political" / "federal_spending.json")
    inflation_data = load_json(ROOT / "data" / "inflation_crosscheck.json")

    if spending_data is None:
        st.info("Federal spending data not found. Run: `python fetch_usaspending.py`")
    else:
        st.markdown("### Federal UI Program Spending (CFDA 17.225)")
        by_state = spending_data.get("spending_by_state", {})

        rows = []
        for state, fy_data in by_state.items():
            for fy, programs in fy_data.items():
                for cfda, info in programs.items():
                    rows.append({
                        "State": state, "Fiscal Year": int(fy), "CFDA": cfda,
                        "Program": info.get("program"),
                        "Obligated ($)": info.get("obligated_amount"),
                    })
        if rows:
            spend_df = pd.DataFrame(rows)
            fig_spend = px.bar(
                spend_df[spend_df["CFDA"] == "17.225"].dropna(subset=["Obligated ($)"]),
                x="Fiscal Year", y="Obligated ($)", color="State",
                barmode="group",
                color_discrete_map={"MD": BLUE, "VA": GREEN, "DC": GOLD},
                title="Federal UI Grants to States (CFDA 17.225)",
            )
            fig_spend.update_layout(**LAYOUT)
            st.plotly_chart(fig_spend, use_container_width=True)
            st.dataframe(spend_df, use_container_width=True)

    if inflation_data:
        st.markdown("---")
        st.markdown("### Inflation Cross-Check (BLS vs FRED)")
        crosscheck = inflation_data.get("crosscheck", {})
        if crosscheck:
            for jur, data in crosscheck.items():
                flag = data.get("flag", "")
                color = CRIMSON if flag == "REVIEW" else GREEN
                delta = data.get("national_vs_metro_delta_pct")
                delta_str = f"{delta:+.2f}%" if delta is not None else "N/A"
                st.markdown(
                    f"**{jur}**: BLS vs DC-metro CPI delta = "
                    f"<span style='color:{color}'>{delta_str}</span> "
                    f"<span style='color:{MUTED}'>[{flag}]</span>",
                    unsafe_allow_html=True,
                )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 5: Data Sources
# ════════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("### Data Source Registry")

    sources = [
        {"Source": "BLS QCEW", "Data": "Average annual wages by state",
         "File": "data/dmv_macro_baselines.csv", "Script": "fetch_bls_baselines.py",
         "API": "api.bls.gov", "Key": "BLS_API_KEY (optional)"},
        {"Source": "BLS LAUS", "Data": "State + county unemployment rates",
         "File": "data/dmv_macro_baselines.csv, data/county_data.json",
         "Script": "fetch_bls_baselines.py, fetch_county_data.py",
         "API": "api.bls.gov", "Key": "BLS_API_KEY (optional)"},
        {"Source": "Census ACS 2022", "Data": "Median household income (state + county)",
         "File": "data/county_data.json, data/political/census_income.json",
         "Script": "fetch_county_data.py, political_layer_analyzer.py",
         "API": "api.census.gov", "Key": "CENSUS_API_KEY"},
        {"Source": "HUD FMR", "Data": "Fair Market Rents (weekly housing proxy)",
         "File": "data/dmv_macro_baselines.csv",
         "Script": "fetch_housing.py", "API": "huduser.gov/hudapi", "Key": "HUD_TOKEN"},
        {"Source": "FRED (St. Louis Fed)", "Data": "CPI crosscheck — national + DC metro",
         "File": "data/inflation_crosscheck.json",
         "Script": "fetch_fred_inflation.py", "API": "api.stlouisfed.org", "Key": "FRED_API_KEY"},
        {"Source": "DOL ETA-5159", "Data": "SUI employer tax rates by state",
         "File": "data/sui_rates.json",
         "Script": "fetch_dol_sui_rates.py", "API": "oui.doleta.gov (CSV)", "Key": "None"},
        {"Source": "FEC", "Data": "Campaign finance (2024 cycle)",
         "File": "data/political/fec_funding_profiles.json",
         "Script": "fec_integration_v251d.py", "API": "api.open.fec.gov", "Key": "FEC_API_KEY"},
        {"Source": "Congress.gov", "Data": "Member list + committee assignments",
         "File": "data/political/political_layer_report.json",
         "Script": "political_layer_builder.py", "API": "api.congress.gov", "Key": "DEMO_KEY"},
        {"Source": "USASpending.gov", "Data": "Federal UI program grants (CFDA 17.225)",
         "File": "data/political/federal_spending.json",
         "Script": "fetch_usaspending.py", "API": "api.usaspending.gov", "Key": "None"},
    ]

    st.dataframe(pd.DataFrame(sources), use_container_width=True)

    st.markdown("---")
    st.markdown("### Data Freshness")
    for fname, label in [
        ("data/dmv_macro_baselines.csv", "Macro baselines"),
        ("data/cpi_annual.json", "CPI data"),
        ("data/inflation_crosscheck.json", "FRED inflation"),
        ("data/county_data.json", "County data"),
        ("data/sui_rates.json", "SUI rates"),
        ("data/political/fec_funding_profiles.json", "FEC profiles"),
        ("data/political/federal_spending.json", "Federal spending"),
    ]:
        path = ROOT / fname
        if path.exists():
            import os
            from datetime import datetime
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            st.markdown(f"- **{label}**: last updated {mtime.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.markdown(f"- **{label}**: <span style='color:{CRIMSON}'>not found</span>",
                        unsafe_allow_html=True)
