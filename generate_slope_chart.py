"""
Fig 1.3 — Slope Chart: Living Wage Coverage Collapse (2010 → 2018 → 2026)
Three states, three time points. Shows the descent in living wage coverage
and the crossing of the 50% survival reference line.
"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
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

JURI_COLORS = {"Maryland": BLUE, "Virginia": GREEN, "District of Columbia": GOLD}
JURI_SHORT  = {"Maryland": "MD", "Virginia": "VA", "District of Columbia": "DC"}

YEARS = [2010, 2018, 2026]

try:
    with open("data/col_bai_results.json") as f:
        raw = json.load(f)
    records = raw["data"]
except Exception as e:
    print(f"⚠ Could not load col_bai_results.json: {e}. Using hardcoded fallback.")
    records = [
        {"jurisdiction": "Maryland",           "year": 2010, "living_wage_coverage_pct": 77.1, "bai": 1.458},
        {"jurisdiction": "Maryland",           "year": 2018, "living_wage_coverage_pct": 60.1, "bai": 1.162},
        {"jurisdiction": "Maryland",           "year": 2026, "living_wage_coverage_pct": 46.4, "bai": 0.956},
        {"jurisdiction": "Virginia",           "year": 2010, "living_wage_coverage_pct": 73.7, "bai": 1.400},
        {"jurisdiction": "Virginia",           "year": 2018, "living_wage_coverage_pct": 57.5, "bai": 1.096},
        {"jurisdiction": "Virginia",           "year": 2026, "living_wage_coverage_pct": 50.0, "bai": 1.024},
        {"jurisdiction": "District of Columbia","year": 2010, "living_wage_coverage_pct": 54.1, "bai": 0.945},
        {"jurisdiction": "District of Columbia","year": 2018, "living_wage_coverage_pct": 53.8, "bai": 0.965},
        {"jurisdiction": "District of Columbia","year": 2026, "living_wage_coverage_pct": 40.5, "bai": 0.854},
    ]

# Organise by jurisdiction
data = {}
for rec in records:
    j = rec["jurisdiction"]
    data.setdefault(j, {})[rec["year"]] = {
        "coverage": rec["living_wage_coverage_pct"],
        "bai":      rec["bai"],
    }

fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG2)

# Reference line at 50%
ax.axhline(50, color=CRIMSON, linewidth=1.2, linestyle="--", alpha=0.6, zorder=1)
ax.text(2026.2, 50.8, "50% reference\n(half of survival costs covered)",
        color=CRIMSON, fontsize=8, va="bottom", fontfamily="monospace", alpha=0.85)

# Reference line at 100%
ax.axhline(100, color=GRID, linewidth=0.8, linestyle=":", alpha=0.5, zorder=1)

for juri, ydata in data.items():
    col  = JURI_COLORS[juri]
    abbr = JURI_SHORT[juri]
    ys   = [ydata[yr]["coverage"] for yr in YEARS]

    # Draw connecting lines
    ax.plot(YEARS, ys, color=col, linewidth=2.8, zorder=3,
            path_effects=[pe.Stroke(linewidth=4.5, foreground=BG2, alpha=0.7), pe.Normal()])

    # Draw dots at each year
    ax.scatter(YEARS, ys, color=col, s=90, zorder=5, edgecolors=BG, linewidths=1.5)

    # Left label (2010)
    ax.text(2009.6, ys[0], f"{abbr}  {ys[0]:.1f}%",
            ha="right", va="center", color=col,
            fontsize=10, fontweight="bold", fontfamily="monospace")

    # Right label (2026)
    delta = ys[2] - ys[0]
    sign  = "▼" if delta < 0 else "▲"
    ax.text(2026.4, ys[2], f"{ys[2]:.1f}%  {sign}{abs(delta):.1f}pp",
            ha="left", va="center", color=col,
            fontsize=10, fontweight="bold", fontfamily="monospace")

    # Middle annotation (2018)
    ax.text(2018, ys[1] + 1.8, f"{ys[1]:.1f}%",
            ha="center", va="bottom", color=col, fontsize=8.5, fontfamily="monospace")

# Formatting
ax.set_xlim(2006, 2030)
ax.set_ylim(30, 90)
ax.set_xticks(YEARS)
ax.set_xticklabels(["2010", "2018", "2026"], color=FG, fontsize=12, fontfamily="monospace")
ax.set_yticks([40, 50, 60, 70, 80])
ax.set_yticklabels([f"{v}%" for v in [40, 50, 60, 70, 80]], color=MUTED, fontsize=9)
ax.tick_params(length=0)
ax.spines[:].set_color(GRID)
ax.grid(color=GRID, linewidth=0.5, linestyle="--", alpha=0.5, axis="y")

ax.set_title(
    "Living Wage Coverage Collapse — 2010 / 2018 / 2026",
    color=LIME, fontsize=14, fontweight="bold", fontfamily="monospace", pad=14
)
ax.set_ylabel("UI Max Benefit as % of MIT Living Wage", color=MUTED, fontsize=10)

ax.text(0.5, -0.08,
        "Sources: MIT Living Wage Calculator 2024 · DOL State Benefit Schedules · col_bai_results.json",
        transform=ax.transAxes, ha="center", fontsize=7.5, color=MUTED, fontfamily="monospace")

plt.tight_layout()
out = Path("figures") / "16_slope_coverage_collapse.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"✅ Saved {out}")
