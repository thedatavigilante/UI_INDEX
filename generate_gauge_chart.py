"""
Fig 1.4 — Gauge Panel: Current BAI vs. Survival Threshold (2026)
Three gauges side-by-side (DC / MD / VA), each showing BAI and COL-BAI.
Needle points to the current value; red zone = below 1.0.
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import math

BG      = "#121212"
BG2     = "#1e1e1e"
GRID    = "#2a2a2a"
FG      = "#e8e8e8"
MUTED   = "#888888"
GREEN   = "#00FF41"
LIME    = "#BFFF00"
GOLD    = "#D4AF37"
CRIMSON = "#DC143C"
BLUE    = "#4aa8d8"
ORANGE  = "#F39C12"

JURI_COLORS = {"DC": GOLD, "MD": BLUE, "VA": GREEN}
JURI_FULL   = {"DC": "District of Columbia", "MD": "Maryland", "VA": "Virginia"}

try:
    with open("data/col_bai_results.json") as f:
        raw = json.load(f)
    records = raw["data"]
except Exception as e:
    print(f"⚠ Fallback: {e}")
    records = [
        {"jurisdiction": "Maryland",            "year": 2026, "bai": 0.956, "col_bai": 0.883},
        {"jurisdiction": "Virginia",            "year": 2026, "bai": 1.024, "col_bai": 0.989},
        {"jurisdiction": "District of Columbia","year": 2026, "bai": 0.854, "col_bai": 0.718},
    ]

lookup_2026 = {}
for rec in records:
    if rec["year"] == 2026:
        abbr = next((k for k, v in JURI_FULL.items() if v == rec["jurisdiction"]), None)
        if abbr:
            lookup_2026[abbr] = rec

output_dir = Path("figures")
output_dir.mkdir(exist_ok=True)

GAUGE_MIN = 0.5
GAUGE_MAX = 1.6
THRESHOLD = 1.0

def draw_gauge(ax, bai_val, col_bai_val, abbr, jcolor):
    """Draw a half-circle gauge with two needles (BAI and COL-BAI)."""
    ax.set_facecolor(BG2)
    ax.set_aspect("equal")
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-0.25, 1.25)
    ax.axis("off")

    # Color zones: red = 0.5–1.0, gold = 1.0–1.2, green = 1.2–1.6
    zones = [
        (GAUGE_MIN, THRESHOLD,   CRIMSON, 0.5),
        (THRESHOLD, 1.25,        GOLD,    0.4),
        (1.25,      GAUGE_MAX,   GREEN,   0.4),
    ]

    def val_to_angle(v):
        norm = (v - GAUGE_MIN) / (GAUGE_MAX - GAUGE_MIN)
        return math.pi * (1 - norm)  # π (left) → 0 (right)

    # Draw arc zones
    for vmin, vmax, zcol, zalpha in zones:
        a_start = math.degrees(val_to_angle(vmax))
        a_end   = math.degrees(val_to_angle(vmin))
        arc = mpatches.Wedge(
            center=(0, 0), r=1.1, theta1=a_start, theta2=a_end,
            width=0.28, color=zcol, alpha=zalpha
        )
        ax.add_patch(arc)

    # Threshold tick at 1.0
    ang_thresh = val_to_angle(THRESHOLD)
    ax.plot([0.82 * math.cos(ang_thresh), 1.12 * math.cos(ang_thresh)],
            [0.82 * math.sin(ang_thresh), 1.12 * math.sin(ang_thresh)],
            color=FG, linewidth=2.5, zorder=5)
    ax.text(1.22 * math.cos(ang_thresh), 1.22 * math.sin(ang_thresh) + 0.04,
            "1.0\nthreshold", ha="center", va="bottom", fontsize=7,
            color=FG, fontfamily="monospace")

    # Tick marks at GAUGE_MIN, 0.75, 1.0, 1.25, GAUGE_MAX
    for tick_v in [0.5, 0.75, 1.0, 1.25, 1.5, 1.6]:
        ta = val_to_angle(tick_v)
        ax.plot([0.86 * math.cos(ta), 0.96 * math.cos(ta)],
                [0.86 * math.sin(ta), 0.96 * math.sin(ta)],
                color=MUTED, linewidth=1.0)
        if tick_v in (0.5, 0.75, 1.25, 1.6):
            ax.text(0.76 * math.cos(ta), 0.76 * math.sin(ta),
                    f"{tick_v:.2f}", ha="center", va="center",
                    fontsize=6.5, color=MUTED, fontfamily="monospace")

    # Draw BAI needle (solid, jcolor)
    ang_bai = val_to_angle(np.clip(bai_val, GAUGE_MIN, GAUGE_MAX))
    needle_len = 0.80
    ax.annotate("", xy=(needle_len * math.cos(ang_bai), needle_len * math.sin(ang_bai)),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=jcolor, lw=2.5,
                                mutation_scale=16))

    # Draw COL-BAI needle (dashed, lighter)
    ang_col = val_to_angle(np.clip(col_bai_val, GAUGE_MIN, GAUGE_MAX))
    ax.annotate("", xy=(0.68 * math.cos(ang_col), 0.68 * math.sin(ang_col)),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=jcolor, lw=1.8,
                                mutation_scale=12, linestyle="dashed", alpha=0.65))

    # Center hub
    hub = plt.Circle((0, 0), 0.055, color=MUTED, zorder=6)
    ax.add_patch(hub)

    # Value labels
    is_bad = bai_val < THRESHOLD
    ax.text(0, -0.12, f"BAI: {bai_val:.3f}",
            ha="center", va="top", fontsize=11, fontweight="bold",
            color=CRIMSON if is_bad else GREEN, fontfamily="monospace")
    ax.text(0, -0.21, f"COL-BAI: {col_bai_val:.3f}",
            ha="center", va="top", fontsize=8.5,
            color=CRIMSON if col_bai_val < THRESHOLD else GOLD,
            fontfamily="monospace", alpha=0.85)

    # Status badge
    status = "BELOW THRESHOLD" if is_bad else "MARGINAL" if bai_val < 1.1 else "ADEQUATE"
    status_col = CRIMSON if is_bad else GOLD if bai_val < 1.1 else GREEN
    ax.text(0, 0.08,
            f"◉ {status}",
            ha="center", va="center", fontsize=8, fontweight="bold",
            color=status_col, fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=BG2,
                      edgecolor=status_col, alpha=0.85))

    ax.set_title(abbr, color=jcolor, fontsize=15, fontweight="bold",
                 fontfamily="monospace", pad=6)


fig, axes = plt.subplots(1, 3, figsize=(13, 5.5))
fig.patch.set_facecolor(BG)

fig.suptitle(
    "Benefit Adequacy Gauges — 2026 Snapshot (BAI & COL-BAI vs. Survival Threshold)",
    color=LIME, fontsize=13, fontweight="bold", fontfamily="monospace", y=1.01
)

for ax, abbr in zip(axes, ["DC", "MD", "VA"]):
    rec = lookup_2026.get(abbr, {})
    draw_gauge(ax, rec.get("bai", 1.0), rec.get("col_bai", 1.0),
               abbr, JURI_COLORS[abbr])

# Legend
legend_items = [
    mpatches.Patch(color=CRIMSON, alpha=0.7, label="Critical zone (BAI < 1.0)"),
    mpatches.Patch(color=GOLD,    alpha=0.7, label="Marginal zone (1.0 – 1.25)"),
    mpatches.Patch(color=GREEN,   alpha=0.7, label="Adequate zone (> 1.25)"),
]
fig.legend(handles=legend_items, loc="lower center", ncol=3,
           facecolor=BG2, edgecolor=GRID, labelcolor=FG, fontsize=8.5,
           bbox_to_anchor=(0.5, -0.04))

fig.text(0.5, -0.10,
         "BAI = Max Weekly Benefit ÷ Weekly Housing Cost · COL-BAI = BAI adjusted for regional price parity (BEA RPP)\n"
         "Solid needle = BAI · Dashed needle = COL-BAI · Threshold at 1.0 = UI check equals housing cost alone\n"
         "Source: col_bai_results.json · dmv_macro_baselines.csv · BEA Regional Price Parities 2022",
         ha="center", fontsize=7.5, color=MUTED, fontfamily="monospace")

plt.tight_layout()
out = Path("figures") / "22_bai_gauge.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"✅ Saved {out}")
