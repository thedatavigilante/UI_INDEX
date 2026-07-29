"""
Fig 3B.5 — Heatmap: Benefit Adequacy Across the 3×3 Grid (Jurisdiction × Year)
Three sub-heatmaps: BAI, COL-BAI, and Living Wage Coverage %.
Color scale: crimson (failure) → gold (marginal) → green (adequate).
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path

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

YEARS  = [2010, 2018, 2026]
JURIS  = ["DC", "MD", "VA"]
JURI_FULL = {"DC": "District of Columbia", "MD": "Maryland", "VA": "Virginia"}

try:
    with open("data/col_bai_results.json") as f:
        raw = json.load(f)
    records = raw["data"]
except Exception as e:
    print(f"⚠ Fallback: {e}")
    records = [
        {"jurisdiction": "Maryland",            "year": 2010, "bai": 1.458, "col_bai": 1.373, "living_wage_coverage_pct": 77.1},
        {"jurisdiction": "Maryland",            "year": 2018, "bai": 1.162, "col_bai": 1.078, "living_wage_coverage_pct": 60.1},
        {"jurisdiction": "Maryland",            "year": 2026, "bai": 0.956, "col_bai": 0.883, "living_wage_coverage_pct": 46.4},
        {"jurisdiction": "Virginia",            "year": 2010, "bai": 1.400, "col_bai": 1.375, "living_wage_coverage_pct": 73.7},
        {"jurisdiction": "Virginia",            "year": 2018, "bai": 1.096, "col_bai": 1.065, "living_wage_coverage_pct": 57.5},
        {"jurisdiction": "Virginia",            "year": 2026, "bai": 1.024, "col_bai": 0.989, "living_wage_coverage_pct": 50.0},
        {"jurisdiction": "District of Columbia","year": 2010, "bai": 0.945, "col_bai": 0.792, "living_wage_coverage_pct": 54.1},
        {"jurisdiction": "District of Columbia","year": 2018, "bai": 0.965, "col_bai": 0.804, "living_wage_coverage_pct": 53.8},
        {"jurisdiction": "District of Columbia","year": 2026, "bai": 0.854, "col_bai": 0.718, "living_wage_coverage_pct": 40.5},
    ]

# Build lookup dict
lookup = {}
for rec in records:
    j_full = rec["jurisdiction"]
    abbr = next((k for k, v in JURI_FULL.items() if v == j_full), None)
    if abbr:
        lookup[(abbr, rec["year"])] = rec

# Build 3×3 matrices (rows=jurisdictions, cols=years)
# JURIS order: DC, MD, VA (top to bottom matches visual "worst to best" in 2026)
bai_mat      = np.array([[lookup[(j, yr)]["bai"]                      for yr in YEARS] for j in JURIS])
col_bai_mat  = np.array([[lookup[(j, yr)]["col_bai"]                  for yr in YEARS] for j in JURIS])
coverage_mat = np.array([[lookup[(j, yr)]["living_wage_coverage_pct"] for yr in YEARS] for j in JURIS])

# Custom diverging colormap: crimson → gold → lime/green
cmap_rg = mcolors.LinearSegmentedColormap.from_list(
    "rg_audit",
    [(0.0, "#DC143C"), (0.35, "#D4AF37"), (0.65, "#BFFF00"), (1.0, "#00FF41")]
)

METRICS = [
    ("BAI", bai_mat,      0.70, 1.60, 1.0,  "Max WBA ÷ Weekly Housing Cost · Threshold: 1.0"),
    ("COL-BAI", col_bai_mat,  0.65, 1.50, 1.0,  "BAI adjusted by BEA Regional Price Parity · Threshold: 1.0"),
    ("Living Wage\nCoverage %", coverage_mat, 35, 85, 50.0, "UI max benefit as % of MIT Living Wage · Threshold: 50%"),
]

fig, axes = plt.subplots(1, 3, figsize=(14, 5.5))
fig.patch.set_facecolor(BG)
fig.suptitle(
    "Benefit Adequacy Heatmap — DC / MD / VA × 2010 / 2018 / 2026",
    color=LIME, fontsize=14, fontweight="bold", fontfamily="monospace", y=1.01
)

for ax, (label, mat, vmin, vmax, threshold, subtitle) in zip(axes, METRICS):
    ax.set_facecolor(BG2)

    # Normalize threshold within vmin-vmax for color reference
    im = ax.imshow(mat, cmap=cmap_rg, vmin=vmin, vmax=vmax, aspect="auto")

    # Cell annotations
    for ri, j in enumerate(JURIS):
        for ci, yr in enumerate(YEARS):
            val = mat[ri, ci]
            # Determine if this cell is below the failure threshold
            bad = val < threshold
            txt_color = BG if not bad else "#fff"
            cell_val  = f"{val:.1f}%" if "%" in label else f"{val:.3f}"
            ax.text(ci, ri, cell_val, ha="center", va="center",
                    color=txt_color, fontsize=11.5, fontweight="bold",
                    fontfamily="monospace")
            # Small "FAIL" label for cells below threshold
            if bad:
                ax.text(ci, ri + 0.32, "FAIL", ha="center", va="center",
                        color=CRIMSON, fontsize=6.5, fontweight="bold",
                        fontfamily="monospace", alpha=0.9)

    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["2010", "2018", "2026"], color=FG, fontsize=11, fontfamily="monospace")
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(JURIS, color=FG, fontsize=12, fontweight="bold", fontfamily="monospace")
    ax.tick_params(length=0)

    ax.set_title(label, color=LIME, fontsize=12, fontweight="bold",
                 fontfamily="monospace", pad=8)
    ax.text(0.5, -0.12, subtitle, transform=ax.transAxes, ha="center",
            fontsize=7, color=MUTED, fontfamily="monospace")

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, orientation="horizontal", pad=0.04, fraction=0.046)
    cbar.ax.tick_params(colors=MUTED, labelsize=7)
    cbar.outline.set_edgecolor(GRID)

    # Threshold line overlay on colorbar
    norm_thresh = (threshold - vmin) / (vmax - vmin)
    cbar.ax.axvline(norm_thresh, color=CRIMSON, linewidth=1.5, linestyle="--")

fig.text(0.5, -0.06,
         "Source: col_bai_results.json · BEA RPP 2022 · MIT Living Wage Calculator 2024 · DOL Benefit Schedules",
         ha="center", fontsize=7.5, color=MUTED, fontfamily="monospace")

plt.tight_layout()
out = Path("figures") / "19_adequacy_heatmap.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"✅ Saved {out}")
