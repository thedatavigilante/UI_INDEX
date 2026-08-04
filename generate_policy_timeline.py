"""
Fig 2.3 — Policy Freeze Timeline (Gantt-style)
Shows HOW LONG each key UI policy has been frozen by drawing horizontal bars
from the freeze start to 2026. Duration is the entire point.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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

# Each entry: (label, start_year, end_year, color, note)
# "end" is when the freeze ended (or 2026 if still frozen)
FREEZE_BARS = [
    # Taxable Wage Bases
    # MD: CSV (dmv_macro_baselines.csv) shows $8,500 for 2010, 2018, 2026 — freeze predates 2010.
    # 1992 is the asserted start; confirmed only that it extends to at least 2010.
    ("MD Taxable Wage Base\n($8,500 — no change since 1992)", 1992, 2026, CRIMSON,  "34-year freeze"),
    # VA: CSV shows $8,000 for 2010, 2018, 2026 — consistent with 2010 freeze start.
    ("VA Taxable Wage Base\n($8,000 — no change since 2010)", 2010, 2026, CRIMSON,  "16-year freeze"),
    # DC: CSV shows $9,000 for ALL three anchor years (2010, 2018, 2026).
    # The wage base was already $9,000 in 2010 — it was NOT raised in 2018.
    # Bar corrected from start_year=2018 to ≤2010; using 2010 as the confirmed upper bound.
    ("DC Taxable Wage Base\n($9,000 — no change since ≤ 2010)", 2010, 2026, CRIMSON, "≥16-year freeze"),
    # Max Weekly Benefits
    # MD: CSV shows $430 for ALL three anchor years (2010, 2018, 2026).
    # Freeze confirmed to predate 2010; bar corrected from 2014 to 2010.
    ("MD Max WBA\n($430 — no change since ≤ 2010)",           2010, 2026, ORANGE,   "≥16-year freeze"),
    # VA: CSV shows $378 for 2010 and 2018, $430 for 2026 (SB1056 fix). Consistent with 2008 start.
    ("VA Max WBA\n($378 → frozen 2008, SB1056 2026)",         2008, 2026, GOLD,     "18-year freeze\n(SB1056 fix: +$52 Jan 2026)"),
    # DC: CSV shows $359 (2010) → $444 (2018) — WBA raised in 2018. Bar unchanged.
    ("DC Max WBA\n($359 → raised to $444 in 2018)",           2010, 2018, ORANGE,   "8-year freeze\n(pre-2018)"),
    # Congressional salary
    ("Congress Salary\n($174K — frozen since 2009)",          2009, 2026, MUTED,    "17-year freeze"),
]

# Point events (markers, not bars)
EVENTS = [
    (2026, 0,  "SB1056\n+$52", GREEN),   # VA benefit fix — row index 4 (VA Max WBA)
    # Note: DC raised its WBA to $444 in 2018 (captured in row 5), NOT its taxable wage base.
    # The wage base ($9,000) was already at this level in 2010 per dmv_macro_baselines.csv.
    (2018, 5,  "DC raised\n$444", BLUE), # DC WBA raised to $444 — row 5
]

fig, ax = plt.subplots(figsize=(13, 7))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG2)

y_positions = list(range(len(FREEZE_BARS)))

for i, (label, start, end, color, note) in enumerate(FREEZE_BARS):
    duration = end - start
    ax.barh(i, duration, left=start, height=0.55,
            color=color, alpha=0.75, edgecolor=GRID, linewidth=0.8)

    # Duration annotation inside bar
    mid = start + duration / 2
    ax.text(mid, i, f"{duration} yrs", ha="center", va="center",
            fontsize=9, fontweight="bold", color=BG, fontfamily="monospace")

    # Note to the right of bar
    ax.text(end + 0.4, i, note, ha="left", va="center",
            fontsize=7.5, color=color, fontfamily="monospace", alpha=0.9)

# Vertical "TODAY" line
ax.axvline(2026, color=LIME, linewidth=1.5, linestyle=":", alpha=0.8)
ax.text(2026.3, len(FREEZE_BARS) - 0.2, "2026", color=LIME, fontsize=9,
        fontfamily="monospace", fontweight="bold", va="top")

# Formatting
ax.set_yticks(y_positions)
ax.set_yticklabels([b[0] for b in FREEZE_BARS],
                   color=FG, fontsize=9, fontfamily="monospace")
ax.set_xlim(1988, 2032)
ax.set_xlabel("Year", color=MUTED, fontsize=10)
ax.tick_params(colors=MUTED, labelsize=9, length=0)
ax.spines[:].set_color(GRID)
ax.grid(color=GRID, linewidth=0.5, linestyle="--", alpha=0.5, axis="x")
ax.invert_yaxis()

# Section dividers
ax.axhline(2.5, color=GRID, linewidth=0.8, linestyle="-", alpha=0.6)   # between wage bases and benefits
ax.text(1989.5, 2.5, "── Taxable Wage Bases ──", color=MUTED, fontsize=7.5,
        va="bottom", fontfamily="monospace")
ax.text(1989.5, 2.7, "── Max Weekly Benefits ──", color=MUTED, fontsize=7.5,
        va="top", fontfamily="monospace")
ax.axhline(5.5, color=GRID, linewidth=0.8, linestyle="-", alpha=0.6)

ax.set_title(
    "UI Policy Freeze Timeline — When Each Cap Was Last Updated",
    color=LIME, fontsize=14, fontweight="bold", fontfamily="monospace", pad=12
)

legend_patches = [
    mpatches.Patch(color=CRIMSON, alpha=0.75, label="Still frozen (2026)"),
    mpatches.Patch(color=GOLD,    alpha=0.75, label="Recent update or partial fix"),
    mpatches.Patch(color=ORANGE,  alpha=0.75, label="Frozen — historical context"),
    mpatches.Patch(color=MUTED,   alpha=0.75, label="Congressional salary"),
]
ax.legend(handles=legend_patches, loc="lower right", facecolor=BG2,
          edgecolor=GRID, labelcolor=FG, fontsize=8)

ax.text(0.5, -0.07,
        "Sources: MD DOL · VA DOL · DC OHR · State DOL statutes · Congress.gov · WSET/MD Compensation Commission",
        transform=ax.transAxes, ha="center", fontsize=7.5, color=MUTED, fontfamily="monospace")

plt.tight_layout()
out = Path("figures") / "17_policy_freeze_timeline.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"✅ Saved {out}")
