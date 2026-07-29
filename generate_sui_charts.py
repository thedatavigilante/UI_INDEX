"""
Fig 2.2 — SUI Effective Tax Rate Decline (2010 / 2018 / 2026)
Fig 4.4 — Dual-Axis: SUI Rate × Wage Base % Erosion (twinx, per state)

Both charts use data that has full 3×3 coverage and is NEVER visualized elsewhere.
"""
import json
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
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

YEARS  = [2010, 2018, 2026]
JURIS  = ["MD", "VA", "DC"]
STATE_COLORS = {"MD": BLUE, "VA": GREEN, "DC": GOLD}
JURI_FULL = {"DC": "District of Columbia", "MD": "Maryland", "VA": "Virginia"}

# ── Load SUI rates ─────────────────────────────────────────────────────────────
try:
    with open("data/sui_rates.json") as f:
        raw = json.load(f)
    sui_rates = raw["rates"]
except Exception as e:
    print(f"⚠ SUI fallback: {e}")
    sui_rates = {
        "MD": {"2010": 0.031, "2018": 0.023, "2026": 0.026},
        "VA": {"2010": 0.028, "2018": 0.014, "2026": 0.019},
        "DC": {"2010": 0.024, "2018": 0.019, "2026": 0.021},
    }

# ── Load macro baselines for WBI computation ──────────────────────────────────
try:
    with open("data/dmv_macro_baselines.csv") as f:
        rows = list(csv.DictReader(f))
    macro = {}
    for r in rows:
        abbr = "DC" if "Columbia" in r["Jurisdiction"] else r["Jurisdiction"][:2]
        macro[(abbr, int(r["Year"]))] = r
except Exception as e:
    print(f"⚠ Macro fallback: {e}")
    macro = {}

HARDCODED_WBI = {
    "DC": {2010: 12.2, 2018: 10.4, 2026: 8.0},
    "MD": {2010: 16.6, 2018: 13.9, 2026: 11.8},
    "VA": {2010: 16.5, 2018: 14.0, 2026: 11.8},
}

def wbi(abbr, year):
    key = (abbr, year)
    if key in macro:
        r = macro[key]
        return float(r["Taxable_Wage_Base"]) / float(r["Avg_Annual_Wage"]) * 100
    return HARDCODED_WBI[abbr][year]

output_dir = Path("figures")
output_dir.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────────
# FIG 23 — SUI Effective Tax Rate Decline (dot-connected multi-line)
# ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG2)

for abbr in JURIS:
    col  = STATE_COLORS[abbr]
    rates = [sui_rates[abbr][str(yr)] * 100 for yr in YEARS]

    ax.plot(YEARS, rates, color=col, linewidth=2.5, marker="o",
            markersize=9, markeredgecolor=BG, markeredgewidth=1.5,
            label=abbr, zorder=3)

    # Annotate each point
    for yr, rate in zip(YEARS, rates):
        offset = 0.05 if abbr == "MD" else (-0.12 if abbr == "VA" else 0.05)
        ax.text(yr, rate + offset + 0.05,
                f"{rate:.1f}%", ha="center", va="bottom",
                fontsize=8.5, fontweight="bold", color=col, fontfamily="monospace")

    # Change annotation from 2010→2026
    delta = rates[-1] - rates[0]
    ax.text(2026.4, rates[-1],
            f"{'+' if delta > 0 else ''}{delta:.1f}pp",
            va="center", ha="left", fontsize=8.5, color=col, fontfamily="monospace")

ax.set_xlim(2007, 2029)
ax.set_xticks(YEARS)
ax.set_xticklabels(["2010", "2018", "2026"], color=FG, fontsize=11, fontfamily="monospace")
ax.set_ylabel("Effective Employer SUI Tax Rate (%)", color=MUTED, fontsize=10)
ax.tick_params(colors=MUTED, labelsize=9, length=0)
ax.spines[:].set_color(GRID)
ax.grid(color=GRID, linewidth=0.5, linestyle="--", alpha=0.6, axis="y")

ax.set_title("Effective Employer SUI Tax Rate Decline — 2010 / 2018 / 2026",
             color=LIME, fontsize=13, fontweight="bold", fontfamily="monospace", pad=12)
ax.legend(facecolor=BG2, edgecolor=GRID, labelcolor=FG, fontsize=10)

ax.text(0.5, -0.1,
        "Source: DOL ETA-5159 State UI Financial Data (effective rate = total contributions ÷ total taxable wages)\n"
        "Note: 2026 row uses 2023 data (latest full published year from DOL).",
        transform=ax.transAxes, ha="center", fontsize=7.5, color=MUTED, fontfamily="monospace")

plt.tight_layout()
plt.savefig(output_dir / "23_sui_rate_decline.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ Saved figures/23_sui_rate_decline.png")

# ─────────────────────────────────────────────────────────────────────
# FIG 24 — Dual-Axis: SUI Rate × WBI (wage base %) per state, 3 panels
# ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 5.5), sharey=False)
fig.patch.set_facecolor(BG)
fig.suptitle(
    "Trust Fund Double-Erosion: SUI Rate AND Wage Base Fraction Both Declining",
    color=LIME, fontsize=13, fontweight="bold", fontfamily="monospace", y=1.01
)

for ax, abbr in zip(axes, JURIS):
    col = STATE_COLORS[abbr]

    rates  = [sui_rates[abbr][str(yr)] * 100 for yr in YEARS]
    wbis   = [wbi(abbr, yr) for yr in YEARS]

    ax.set_facecolor(BG2)
    ax2 = ax.twinx()
    ax2.set_facecolor(BG2)

    # Left axis: SUI rate (solid line)
    l1, = ax.plot(YEARS, rates, color=col, linewidth=2.5, marker="o",
                  markersize=8, markeredgecolor=BG, markeredgewidth=1.5,
                  label="SUI Rate (%)", zorder=3)
    for yr, r in zip(YEARS, rates):
        ax.text(yr, r + 0.12, f"{r:.1f}%", ha="center", va="bottom",
                fontsize=8, color=col, fontfamily="monospace", fontweight="bold")

    # Right axis: WBI (dashed line, CRIMSON)
    l2, = ax2.plot(YEARS, wbis, color=CRIMSON, linewidth=2.2, linestyle="--",
                   marker="s", markersize=7, markeredgecolor=BG, markeredgewidth=1.2,
                   label="WBI: Wage Base as % of Avg Wage", zorder=3)
    for yr, w in zip(YEARS, wbis):
        ax2.text(yr, w + 0.3, f"{w:.1f}%", ha="center", va="bottom",
                 fontsize=8, color=CRIMSON, fontfamily="monospace", fontweight="bold")

    # Formatting
    ax.set_xlim(2007, 2029)
    ax.set_xticks(YEARS)
    ax.set_xticklabels(["2010", "2018", "2026"], color=FG, fontsize=10, fontfamily="monospace")
    ax.tick_params(colors=MUTED, labelsize=8.5, length=0)
    ax2.tick_params(colors=CRIMSON, labelsize=8.5, length=0)
    ax.spines[:].set_color(GRID)
    ax2.spines[:].set_color(GRID)
    ax.grid(color=GRID, linewidth=0.5, linestyle="--", alpha=0.5, axis="y")

    if JURIS.index(abbr) == 0:
        ax.set_ylabel("Effective SUI Rate (%)", color=col, fontsize=9)
    if JURIS.index(abbr) == 2:
        ax2.set_ylabel("Wage Base as % of Avg Wage", color=CRIMSON, fontsize=9)

    ax.yaxis.label.set_color(col)
    ax2.yaxis.label.set_color(CRIMSON)

    ax.set_title(abbr, color=col, fontsize=13, fontweight="bold", fontfamily="monospace", pad=8)

    # Shared legend for first panel
    if JURIS.index(abbr) == 1:
        ax.legend([l1, l2], ["SUI Rate (left axis)", "Wage Base % (right axis)"],
                  facecolor=BG2, edgecolor=GRID, labelcolor=FG, fontsize=8,
                  loc="upper right")

fig.text(0.5, -0.05,
         "Both metrics declining simultaneously = compounding trust fund starvation.\n"
         "Source: DOL ETA-5159 (SUI rates) · BLS QCEW (avg wages) · State DOL (wage base statutes)",
         ha="center", fontsize=7.5, color=MUTED, fontfamily="monospace")

plt.tight_layout()
plt.savefig(output_dir / "24_sui_wagbase_dual.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ Saved figures/24_sui_wagbase_dual.png")

print("\n✅ Both SUI charts generated.")
