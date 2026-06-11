import csv
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from pathlib import Path

# ── Brand palette ──────────────────────────────────────────────────────────────
BG       = "#121212"
BG2      = "#1e1e1e"
GRID     = "#2a2a2a"
FG       = "#e8e8e8"
MUTED    = "#888888"
GREEN    = "#00FF41"
LIME     = "#BFFF00"
GOLD     = "#D4AF37"
CRIMSON  = "#DC143C"
BLUE     = "#4aa8d8"
ORANGE   = "#F39C12"

STATE_COLORS = {
    "Maryland":          BLUE,
    "Virginia":          GREEN,
    "District of Columbia": GOLD,
}

def apply_dark_style(ax, title, xlabel=None, ylabel=None):
    ax.set_facecolor(BG2)
    ax.figure.patch.set_facecolor(BG)
    ax.set_title(title, color=LIME, fontsize=13, fontweight="bold",
                 fontfamily="monospace", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, color=MUTED, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, color=MUTED, fontsize=10)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.spines[:].set_color(GRID)
    ax.grid(color=GRID, linewidth=0.6, linestyle="--", alpha=0.7)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)

# ── Load data ──────────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent / "data" / "dmv_macro_baselines.csv"
records = []
with open(DATA_PATH, "r", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append({
            "Jurisdiction": row["Jurisdiction"],
            "Year": int(row["Year"]),
            "Max_WBA": float(row["Max_WBA"]),
            "Taxable_Wage_Base": float(row["Taxable_Wage_Base"]),
            "Avg_Annual_Wage": float(row["Avg_Annual_Wage"]),
            "Weekly_Housing": float(row["Weekly_Housing"]),
        })

for rec in records:
    rec["BAI"]         = rec["Max_WBA"] / rec["Weekly_Housing"]
    rec["WBI"]         = rec["Taxable_Wage_Base"] / rec["Avg_Annual_Wage"]
    net_counted        = max(0, 250 - 50)
    rec["MIPI"]        = net_counted / rec["Max_WBA"]
    rec["Housing_Gap"] = rec["Weekly_Housing"] - rec["Max_WBA"]

df = pd.DataFrame(records)

FIG_DIR = Path(__file__).parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

# ── Figure 01: BAI Decay Trajectory ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
apply_dark_style(ax, "BAI Decay Trajectory: 2010 → 2026",
                 xlabel="Year", ylabel="Benefit Adequacy Index (BAI)")

for jurisdiction in df["Jurisdiction"].unique():
    sub = df[df["Jurisdiction"] == jurisdiction].sort_values("Year")
    color = STATE_COLORS[jurisdiction]
    ax.plot(sub["Year"], sub["BAI"], marker="o", linewidth=2.5, markersize=8,
            label=jurisdiction, color=color)
    # Annotate 2026 endpoint
    last = sub.iloc[-1]
    ax.annotate(f"{last['BAI']:.2f}", xy=(last["Year"], last["BAI"]),
                xytext=(6, 0), textcoords="offset points",
                color=color, fontsize=9, fontweight="bold")

ax.axhline(1.0, color=CRIMSON, linestyle="--", linewidth=1.5, alpha=0.85,
           label="Survival Threshold (1.0)")
ax.fill_between([2009, 2027], 0.5, 1.0, color=CRIMSON, alpha=0.04)
ax.set_ylim(0.5, 1.6)
ax.set_xlim(2009, 2027)
ax.set_xticks([2010, 2018, 2026])

legend = ax.legend(title="Jurisdiction", facecolor=BG2, edgecolor=GRID,
                   labelcolor=FG, title_fontsize=9, fontsize=9)
legend.get_title().set_color(MUTED)

plt.tight_layout()
plt.savefig(FIG_DIR / "01_bai_decay_trajectory.png", dpi=150, bbox_inches="tight",
            facecolor=BG)
plt.close()
print("✅ Figure 01 saved")

# ── Figure 02: WBI Stagnation ──────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
apply_dark_style(ax, "WBI Stagnation: Flat SUI Caps vs. Rising Wages",
                 xlabel="Year", ylabel="Wage Base as % of Avg Annual Wage")

for jurisdiction in df["Jurisdiction"].unique():
    sub = df[df["Jurisdiction"] == jurisdiction].sort_values("Year")
    color = STATE_COLORS[jurisdiction]
    ax.plot(sub["Year"], sub["WBI"] * 100, marker="s", linewidth=2.5, markersize=8,
            label=jurisdiction, color=color)
    last = sub.iloc[-1]
    ax.annotate(f"{last['WBI']*100:.1f}%", xy=(last["Year"], last["WBI"]*100),
                xytext=(6, 0), textcoords="offset points",
                color=color, fontsize=9, fontweight="bold")

ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))
ax.set_xlim(2009, 2027)
ax.set_xticks([2010, 2018, 2026])

legend = ax.legend(title="Jurisdiction", facecolor=BG2, edgecolor=GRID,
                   labelcolor=FG, title_fontsize=9, fontsize=9)
legend.get_title().set_color(MUTED)

plt.tight_layout()
plt.savefig(FIG_DIR / "02_wbi_stagnation.png", dpi=150, bbox_inches="tight",
            facecolor=BG)
plt.close()
print("✅ Figure 02 saved")

# ── Figure 03: MIPI Clawback ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
apply_dark_style(ax, "MIPI Clawback Severity at $250 Side-Hustle Earnings",
                 xlabel="Year", ylabel="Multi-Income Penalty Index (MIPI)")

for jurisdiction in df["Jurisdiction"].unique():
    sub = df[df["Jurisdiction"] == jurisdiction].sort_values("Year")
    color = STATE_COLORS[jurisdiction]
    ax.plot(sub["Year"], sub["MIPI"], marker="^", linewidth=2.5, markersize=8,
            label=jurisdiction, color=color)
    last = sub.iloc[-1]
    ax.annotate(f"{last['MIPI']:.2f}", xy=(last["Year"], last["MIPI"]),
                xytext=(6, 0), textcoords="offset points",
                color=color, fontsize=9, fontweight="bold")

ax.set_xlim(2009, 2027)
ax.set_xticks([2010, 2018, 2026])

legend = ax.legend(title="Jurisdiction", facecolor=BG2, edgecolor=GRID,
                   labelcolor=FG, title_fontsize=9, fontsize=9)
legend.get_title().set_color(MUTED)

plt.tight_layout()
plt.savefig(FIG_DIR / "03_mipi_clawback.png", dpi=150, bbox_inches="tight",
            facecolor=BG)
plt.close()
print("✅ Figure 03 saved")

# ── Figure 04: Housing Cost vs. WBA Gap (REDESIGNED) ──────────────────────────
# Show WBA (frozen/flat) and Housing Cost (rising) as separate line pairs per state.
# The visual divergence IS the story — a flat line and a rising line separating over time.
fig, axes = plt.subplots(1, 3, figsize=(13, 5), sharey=True)
fig.patch.set_facecolor(BG)

jurisdictions = ["Maryland", "Virginia", "District of Columbia"]
labels        = ["Maryland", "Virginia", "DC"]

for i, (jurisdiction, label) in enumerate(zip(jurisdictions, labels)):
    ax = axes[i]
    ax.set_facecolor(BG2)
    sub = df[df["Jurisdiction"] == jurisdiction].sort_values("Year")
    color = STATE_COLORS[jurisdiction]

    ax.plot(sub["Year"], sub["Weekly_Housing"], color=CRIMSON, marker="o",
            linewidth=2.5, markersize=7, label="Housing Cost", zorder=3)
    ax.plot(sub["Year"], sub["Max_WBA"], color=color, marker="s",
            linewidth=2.5, markersize=7, linestyle="--", label="Max WBA", zorder=3)

    # Shade the gap
    ax.fill_between(sub["Year"], sub["Max_WBA"], sub["Weekly_Housing"],
                    where=sub["Weekly_Housing"] >= sub["Max_WBA"],
                    alpha=0.18, color=CRIMSON, label="Survival Deficit")

    # Annotate 2026 gap
    row_2026 = sub[sub["Year"] == 2026].iloc[0]
    gap = row_2026["Weekly_Housing"] - row_2026["Max_WBA"]
    mid = (row_2026["Weekly_Housing"] + row_2026["Max_WBA"]) / 2
    ax.annotate(f"−${gap:.0f}/wk", xy=(2026, mid), xytext=(-38, 0),
                textcoords="offset points", color=CRIMSON,
                fontsize=9, fontweight="bold")

    ax.set_title(label, color=color, fontsize=12, fontweight="bold",
                 fontfamily="monospace")
    ax.set_xticks([2010, 2018, 2026])
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.spines[:].set_color(GRID)
    ax.grid(color=GRID, linewidth=0.5, linestyle="--", alpha=0.6)

    if i == 0:
        ax.set_ylabel("Weekly Amount ($)", color=MUTED, fontsize=10)
        legend = ax.legend(facecolor=BG2, edgecolor=GRID, labelcolor=FG,
                           fontsize=8, loc="upper left")

fig.suptitle("Housing Cost vs. Maximum Weekly Benefit: The Survival Deficit",
             color=LIME, fontsize=13, fontweight="bold", fontfamily="monospace", y=1.02)
plt.tight_layout()
plt.savefig(FIG_DIR / "04_housing_vs_wba_gap.png", dpi=150, bbox_inches="tight",
            facecolor=BG)
plt.close()
print("✅ Figure 04 saved (redesigned: 3-panel diverging lines)")

print(f"\n✅ All 4 core figures regenerated in {FIG_DIR}")
