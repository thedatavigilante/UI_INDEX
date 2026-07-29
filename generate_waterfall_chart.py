"""
Fig 3B.3 — Waterfall: Cumulative Expense Drain per Jurisdiction (2026)
Starts at the UI max benefit and waterfall-subtracts each expense category
to show the running balance. DC goes negative at housing alone.
"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

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

CATEGORIES = ["housing", "food", "transportation", "healthcare", "other"]
CAT_LABELS = ["Housing", "Food", "Transportation", "Healthcare", "Other"]
CAT_COLORS = [CRIMSON, ORANGE, GOLD, BLUE, MUTED]

try:
    with open("data/col_bai_results.json") as f:
        raw = json.load(f)
    summary = raw["summary_2026"]
except Exception as e:
    print(f"⚠ Fallback: {e}")
    summary = {
        "Maryland":             {"max_wba": 430.0, "expense_breakdown": {"housing":337,"food":90,"transportation":127,"healthcare":46,"childcare":0,"other":75}},
        "Virginia":             {"max_wba": 430.0, "expense_breakdown": {"housing":285,"food":85,"transportation":130,"healthcare":43,"childcare":0,"other":70}},
        "District of Columbia": {"max_wba": 444.0, "expense_breakdown": {"housing":476,"food":96,"transportation":139,"healthcare":52,"childcare":0,"other":86}},
    }

JURISDICTIONS = [
    ("District of Columbia", "DC", GOLD),
    ("Maryland",             "MD", BLUE),
    ("Virginia",             "VA", GREEN),
]

fig, axes = plt.subplots(1, 3, figsize=(15, 7), sharey=False)
fig.patch.set_facecolor(BG)
fig.suptitle(
    "Cumulative Expense Drain — Where the UI Check Goes (2026)",
    color=LIME, fontsize=14, fontweight="bold", fontfamily="monospace", y=1.01
)

for ax, (juri_full, abbr, jcolor) in zip(axes, JURISDICTIONS):
    ax.set_facecolor(BG2)

    jdata   = summary[juri_full]
    wba     = jdata["max_wba"]
    expenses = jdata["expense_breakdown"]

    # Build waterfall: first bar = WBA (positive), then each expense (negative)
    steps      = ["UI Max\nBenefit"] + CAT_LABELS
    amounts    = [wba] + [-expenses.get(c, 0) for c in CATEGORIES]
    bar_colors = [GREEN] + CAT_COLORS
    bar_labels = [f"+${wba:.0f}"] + [f"−${expenses.get(c,0)}" for c in CATEGORIES]

    # Compute running total (bottom of each bar in waterfall)
    running = 0
    bottoms = []
    heights = []
    for amt in amounts:
        if amt >= 0:
            bottoms.append(0)
            heights.append(amt)
        else:
            running_new = running + amt
            bottoms.append(min(running, running_new))
            heights.append(abs(amt))
        running += amt

    # Recalculate using true waterfall logic:
    running = 0
    bottoms2 = []
    heights2 = []
    for amt in amounts:
        if amt >= 0:
            bottoms2.append(0)
            heights2.append(amt)
            running = amt
        else:
            new_running = running + amt
            bottoms2.append(min(running, new_running))
            heights2.append(abs(amt))
            running = new_running

    x_pos = range(len(steps))

    for xi, (bot, hgt, col, lbl) in enumerate(zip(bottoms2, heights2, bar_colors, bar_labels)):
        ax.bar(xi, hgt, bottom=bot, color=col, alpha=0.82,
               edgecolor=GRID, linewidth=0.8, width=0.6)

        # Label value above/on bar
        val_y = bot + hgt + 4
        ax.text(xi, val_y, lbl, ha="center", va="bottom",
                fontsize=9, fontweight="bold", color=col, fontfamily="monospace")

    # Connector lines
    running = wba
    for xi in range(1, len(steps)):
        amt = amounts[xi]
        new_running = running + amt
        ax.plot([xi - 0.3, xi + 0.3], [running, running],
                color=GRID, linewidth=1.0, linestyle="--", alpha=0.7)
        running = new_running

    # Zero line
    ax.axhline(0, color=GRID, linewidth=1.0, alpha=0.7)

    # Final balance
    final = wba + sum(amounts[1:])
    final_color = CRIMSON if final < 0 else GREEN
    ax.text(len(steps) - 0.5, max(20, abs(final) + 15),
            f"Balance:\n{'−' if final<0 else '+'}${abs(final):.0f}/wk",
            ha="right", va="bottom", fontsize=9.5, fontweight="bold",
            color=final_color, fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor=BG2, edgecolor=final_color, alpha=0.9))

    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(steps, color=FG, fontsize=8.5, fontfamily="monospace")
    ax.set_ylabel("Weekly Dollars ($)" if abbr == "DC" else "", color=MUTED, fontsize=9)
    ax.tick_params(colors=MUTED, labelsize=8.5, length=0)
    ax.spines[:].set_color(GRID)
    ax.grid(color=GRID, linewidth=0.5, linestyle="--", alpha=0.4, axis="y")

    title_color = CRIMSON if final < 0 else jcolor
    ax.set_title(f"{abbr}  (Max WBA: ${wba:.0f}/wk)",
                 color=title_color, fontsize=12, fontweight="bold",
                 fontfamily="monospace", pad=8)

    if abbr == "DC":
        ax.text(0.03, 0.98,
                "Housing alone\nexceeds the check.",
                transform=ax.transAxes, va="top", ha="left",
                fontsize=8, color=CRIMSON, fontfamily="monospace",
                bbox=dict(boxstyle="round", facecolor=BG2, edgecolor=CRIMSON, alpha=0.9))

legend_patches = [
    mpatches.Patch(color=GREEN,   alpha=0.82, label="UI Max Benefit (starting balance)"),
    mpatches.Patch(color=CRIMSON, alpha=0.82, label="Housing"),
    mpatches.Patch(color=ORANGE,  alpha=0.82, label="Food"),
    mpatches.Patch(color=GOLD,    alpha=0.82, label="Transportation"),
    mpatches.Patch(color=BLUE,    alpha=0.82, label="Healthcare"),
    mpatches.Patch(color=MUTED,   alpha=0.82, label="Other necessities"),
]
fig.legend(handles=legend_patches, loc="lower center", ncol=6,
           facecolor=BG2, edgecolor=GRID, labelcolor=FG, fontsize=8.5,
           bbox_to_anchor=(0.5, -0.06))

fig.text(0.5, -0.12,
         "Source: MIT Living Wage Calculator 2024 (1 adult, no children) · DOL UI Benefit Schedules · col_bai_results.json\n"
         "Expense categories reflect 2024 MIT Living Wage methodology; childcare excluded (1-adult baseline).",
         ha="center", fontsize=7.5, color=MUTED, fontfamily="monospace")

plt.tight_layout()
out = Path("figures") / "25_waterfall_expense_drain.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"✅ Saved {out}")
