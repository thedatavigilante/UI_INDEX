"""
Fig A.1 — Radar/Spider: Multi-Index Severity Profile (2026 vs. 2010 ghost)
Fig A.2 — Small Multiples: All Key Metrics 3×3 Grid (DC/MD/VA × 2010/2018/2026)
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import math

BG      = "#121212"
BG2     = "#1e1e1e"
BG3     = "#252525"
GRID    = "#2a2a2a"
FG      = "#e8e8e8"
MUTED   = "#888888"
GREEN   = "#00FF41"
LIME    = "#BFFF00"
GOLD    = "#D4AF37"
CRIMSON = "#DC143C"
BLUE    = "#4aa8d8"
ORANGE  = "#F39C12"

JURI_COLORS   = {"DC": GOLD, "MD": BLUE, "VA": GREEN}
JURI_FULL     = {"DC": "District of Columbia", "MD": "Maryland", "VA": "Virginia"}
JURIS         = ["DC", "MD", "VA"]
YEARS         = [2010, 2018, 2026]

try:
    with open("data/col_bai_results.json") as f:
        raw = json.load(f)
    records = raw["data"]
except Exception as e:
    print(f"⚠ Fallback: {e}")
    records = [
        {"jurisdiction": "Maryland",            "year": 2010, "bai": 1.458, "col_bai": 1.373, "living_wage_coverage_pct": 77.1, "max_wba": 430, "weekly_housing": 295, "living_wage_gap": 128},
        {"jurisdiction": "Maryland",            "year": 2018, "bai": 1.162, "col_bai": 1.078, "living_wage_coverage_pct": 60.1, "max_wba": 430, "weekly_housing": 370, "living_wage_gap": 286},
        {"jurisdiction": "Maryland",            "year": 2026, "bai": 0.956, "col_bai": 0.883, "living_wage_coverage_pct": 46.4, "max_wba": 430, "weekly_housing": 450, "living_wage_gap": 496},
        {"jurisdiction": "Virginia",            "year": 2010, "bai": 1.400, "col_bai": 1.375, "living_wage_coverage_pct": 73.7, "max_wba": 378, "weekly_housing": 270, "living_wage_gap": 135},
        {"jurisdiction": "Virginia",            "year": 2018, "bai": 1.096, "col_bai": 1.065, "living_wage_coverage_pct": 57.5, "max_wba": 378, "weekly_housing": 345, "living_wage_gap": 279},
        {"jurisdiction": "Virginia",            "year": 2026, "bai": 1.024, "col_bai": 0.989, "living_wage_coverage_pct": 50.0, "max_wba": 430, "weekly_housing": 420, "living_wage_gap": 430},
        {"jurisdiction": "District of Columbia","year": 2010, "bai": 0.945, "col_bai": 0.792, "living_wage_coverage_pct": 54.1, "max_wba": 359, "weekly_housing": 380, "living_wage_gap": 304},
        {"jurisdiction": "District of Columbia","year": 2018, "bai": 0.965, "col_bai": 0.804, "living_wage_coverage_pct": 53.8, "max_wba": 444, "weekly_housing": 460, "living_wage_gap": 381},
        {"jurisdiction": "District of Columbia","year": 2026, "bai": 0.854, "col_bai": 0.718, "living_wage_coverage_pct": 40.5, "max_wba": 444, "weekly_housing": 520, "living_wage_gap": 652},
    ]

try:
    with open("data/sui_rates.json") as f:
        sui_raw = json.load(f)
    sui_rates = sui_raw["rates"]
except Exception:
    sui_rates = {"MD":{"2010":0.031,"2018":0.023,"2026":0.026},
                 "VA":{"2010":0.028,"2018":0.014,"2026":0.019},
                 "DC":{"2010":0.024,"2018":0.019,"2026":0.021}}

try:
    with open("data/dmv_macro_baselines.csv") as f:
        import csv
        rows = list(csv.DictReader(f))
    macro = {(r["Jurisdiction"][:2] if r["Jurisdiction"] != "District of Columbia" else "DC", int(r["Year"])): r
             for r in rows}
except Exception:
    macro = {}

def get_wbi(abbr, year):
    juri_full_name = JURI_FULL[abbr]
    key = (abbr, year)
    if key in macro:
        r = macro[key]
        return float(r["Taxable_Wage_Base"]) / float(r["Avg_Annual_Wage"]) * 100
    hardcoded = {"DC":{"2010":12.2,"2018":10.4,"2026":8.0},
                 "MD":{"2010":16.6,"2018":13.9,"2026":11.8},
                 "VA":{"2010":16.5,"2018":14.0,"2026":11.8}}
    return hardcoded[abbr][str(year)]

lookup = {}
for rec in records:
    abbr = next((k for k, v in JURI_FULL.items() if v == rec["jurisdiction"]), None)
    if abbr:
        lookup[(abbr, rec["year"])] = rec

# ─────────────────────────────────────────────────────────────────────
# FIG A.1 — RADAR CHART
# ─────────────────────────────────────────────────────────────────────
# Axes: BAI (0→2), COL-BAI (0→2), WBI% (0→25%), LW Coverage% (0→100%), SUI rate (0→4%)
# Normalize each to 0–1 range for radar display
RADAR_AXES = [
    ("BAI\n(housing-only)", "bai",              0.60, 1.70),
    ("COL-BAI\n(full basket)", "col_bai",       0.60, 1.50),
    ("WBI\n(wage base %)", "wbi",               6.0,  20.0),
    ("LW Coverage\n(%)", "lw_cov",              35.0, 85.0),
    ("SUI Rate\n(effective)", "sui",             1.2,  3.5),
]

N_AXES = len(RADAR_AXES)
angles = [2 * math.pi * i / N_AXES for i in range(N_AXES)]
angles += angles[:1]  # close the polygon

fig_r, ax_r = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
fig_r.patch.set_facecolor(BG)
ax_r.set_facecolor(BG2)

def get_radar_values(abbr, year):
    rec = lookup.get((abbr, year), {})
    vals = []
    for _, key, vmin, vmax in RADAR_AXES:
        if key == "bai":
            v = rec.get("bai", 1.0)
        elif key == "col_bai":
            v = rec.get("col_bai", 1.0)
        elif key == "wbi":
            v = get_wbi(abbr, year)
        elif key == "lw_cov":
            v = rec.get("living_wage_coverage_pct", 50.0)
        elif key == "sui":
            v = sui_rates.get(abbr, {}).get(str(year), 0.02) * 100
        else:
            v = 0
        # Normalize 0→1
        vals.append((v - vmin) / (vmax - vmin))
    return vals

for abbr in JURIS:
    col = JURI_COLORS[abbr]

    # 2026 solid
    vals_26 = get_radar_values(abbr, 2026)
    vals_26 += vals_26[:1]
    ax_r.plot(angles, vals_26, color=col, linewidth=2.5, label=f"{abbr} 2026")
    ax_r.fill(angles, vals_26, color=col, alpha=0.12)

    # 2010 ghost (dotted, lower alpha)
    vals_10 = get_radar_values(abbr, 2010)
    vals_10 += vals_10[:1]
    ax_r.plot(angles, vals_10, color=col, linewidth=1.2, linestyle=":", alpha=0.45,
              label=f"{abbr} 2010 (ghost)")

# Axis labels
ax_labels = [a[0] for a in RADAR_AXES]
ax_r.set_thetagrids([a * 180 / math.pi for a in angles[:-1]], ax_labels,
                    color=FG, fontsize=9.5, fontfamily="monospace")

# Radial grid
ax_r.set_ylim(0, 1)
ax_r.set_yticks([0.25, 0.5, 0.75, 1.0])
ax_r.set_yticklabels(["25%", "50%", "75%", "100%"], color=MUTED, fontsize=7)
ax_r.yaxis.set_tick_params(labelcolor=MUTED)
ax_r.spines["polar"].set_color(GRID)
ax_r.grid(color=GRID, linewidth=0.6, alpha=0.6)
ax_r.set_facecolor(BG2)

# Failure threshold ring at ~50% of range
ax_r.plot(angles, [0.5] * len(angles), color=CRIMSON, linewidth=1.0,
          linestyle="--", alpha=0.5, label="~Failure threshold (mid-range)")

ax_r.set_title("Multi-Index Severity Radar — 2026 vs. 2010 Ghost",
               color=LIME, fontsize=13, fontweight="bold",
               fontfamily="monospace", pad=22)

legend = ax_r.legend(loc="upper right", bbox_to_anchor=(1.38, 1.12),
                     facecolor=BG2, edgecolor=GRID, labelcolor=FG, fontsize=8.5)

fig_r.text(0.5, 0.02,
           "Axes normalized to comparative range. Larger polygon = stronger performance.\n"
           "BAI: housing-only adequacy · COL-BAI: full-basket adjusted · WBI: taxable wage base % · "
           "LW Coverage: UI vs. MIT Living Wage · SUI: effective employer rate",
           ha="center", fontsize=7.5, color=MUTED, fontfamily="monospace")

plt.tight_layout()
out_r = Path("figures") / "20_radar_severity.png"
plt.savefig(out_r, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"✅ Saved {out_r}")

# ─────────────────────────────────────────────────────────────────────
# FIG A.2 — SMALL MULTIPLES: 3×3 Grid (rows=jurisdictions, cols=years)
# Each cell: mini bar chart of key metrics for that jurisdiction×year
# ─────────────────────────────────────────────────────────────────────
METRICS_SM = [
    ("BAI",        "bai",                    0, 1.6,  1.0,  BLUE),
    ("COL-BAI",    "col_bai",                0, 1.6,  1.0,  LIME[:7]),
    ("LW Cov %",   "living_wage_coverage_pct", 0, 85, 50.0, GOLD),
    ("LW Gap $/wk","living_wage_gap",         0, 700, 0,    CRIMSON),
]

fig_sm = plt.figure(figsize=(14, 10))
fig_sm.patch.set_facecolor(BG)
outer = gridspec.GridSpec(3, 3, figure=fig_sm, hspace=0.55, wspace=0.38)

for ri, abbr in enumerate(JURIS):
    for ci, year in enumerate(YEARS):
        rec = lookup.get((abbr, year), {})
        ax = fig_sm.add_subplot(outer[ri, ci])
        ax.set_facecolor(BG2)

        names  = [m[0] for m in METRICS_SM]
        values = []
        thresholds = []
        bar_cols = []
        for mname, mkey, vmin, vmax, thresh, mcol in METRICS_SM:
            v = rec.get(mkey, 0)
            values.append(v)
            thresholds.append(thresh)
            bar_cols.append(mcol)

        # Normalize values to 0-100 for uniform bar heights
        normed = []
        for val, (_, _, vmin, vmax, _, _) in zip(values, METRICS_SM):
            normed.append(min(1.0, max(0.0, (val - vmin) / (vmax - vmin))) * 100)

        x_pos = range(len(METRICS_SM))
        bars = ax.bar(x_pos, normed, color=bar_cols, alpha=0.75,
                      edgecolor=GRID, linewidth=0.5, width=0.65)

        # Threshold markers
        for xi, (_, _, vmin, vmax, thresh, _) in enumerate(METRICS_SM):
            if thresh > 0:
                t_norm = (thresh - vmin) / (vmax - vmin) * 100
                ax.plot([xi - 0.35, xi + 0.35], [t_norm, t_norm],
                        color=CRIMSON, linewidth=1.2, linestyle="--")

        # Raw value labels
        for xi, (val, (mname, mkey, vmin, vmax, thresh, mcol)) in enumerate(zip(values, METRICS_SM)):
            fmt = f"{val:.0f}%" if "%" in mname or "Cov" in mname else f"{val:.2f}" if val < 10 else f"${val:.0f}"
            bad = val < thresh if thresh > 0 else False
            ax.text(xi, normed[xi] + 2.5, fmt, ha="center", va="bottom",
                    fontsize=7.5, fontweight="bold",
                    color=CRIMSON if bad else FG, fontfamily="monospace")

        ax.set_xticks(list(x_pos))
        ax.set_xticklabels(names, color=MUTED, fontsize=6.5, fontfamily="monospace")
        ax.set_ylim(0, 115)
        ax.set_yticks([])
        ax.tick_params(length=0)
        ax.spines[:].set_color(GRID)

        # Cell title
        cell_col = JURI_COLORS[abbr]
        ax.set_title(f"{abbr}  {year}", color=cell_col, fontsize=9,
                     fontweight="bold", fontfamily="monospace", pad=4)

# Row and column headers
for ri, abbr in enumerate(JURIS):
    fig_sm.text(0.01, 0.83 - ri * 0.3, JURI_FULL[abbr].replace("District of Columbia","DC"),
                va="center", rotation=90, fontsize=10, color=JURI_COLORS[abbr],
                fontfamily="monospace", fontweight="bold")

fig_sm.suptitle(
    "All Key Metrics — Small Multiples Grid (Jurisdiction × Year)",
    color=LIME, fontsize=13, fontweight="bold", fontfamily="monospace", y=1.01
)
fig_sm.text(0.5, -0.03,
            "Bars normalized per metric (0→max). Red dashed line = failure threshold. Values labeled above each bar.\n"
            "Source: col_bai_results.json · dmv_macro_baselines.csv · MIT Living Wage 2024",
            ha="center", fontsize=7.5, color=MUTED, fontfamily="monospace")

out_sm = Path("figures") / "21_small_multiples.png"
plt.savefig(out_sm, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"✅ Saved {out_sm}")
