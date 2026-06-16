import json
from src import DATA, POLITICAL, FIGURES  # repo-root-anchored paths
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

# ── Brand palette ──────────────────────────────────────────────────────────────
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

STATE_COLORS = {"MD": BLUE, "VA": GREEN, "DC": GOLD}

def apply_dark_style(ax, title, xlabel=None, ylabel=None):
    ax.set_facecolor(BG2)
    ax.figure.patch.set_facecolor(BG)
    ax.set_title(title, color=LIME, fontsize=13, fontweight="bold",
                 fontfamily="monospace", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, color=MUTED, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, color=MUTED, fontsize=10)
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.spines[:].set_color(GRID)
    ax.grid(color=GRID, linewidth=0.6, linestyle="--", alpha=0.7, axis="y")

output_dir = FIGURES
output_dir.mkdir(exist_ok=True)

with open(POLITICAL / "employer_contribution_gap.json") as f:
    raw = json.load(f)

# Handle both plain list and _metadata-wrapped formats
gaps = raw.get("data", raw) if isinstance(raw, dict) else raw

states    = [g["state"] for g in gaps]
per_emp   = [g["per_employee_gap"] for g in gaps]
aggregate = [g["aggregate_gap"] / 1e6 for g in gaps]
expected  = [g["expected_wage_base"] for g in gaps]
statutory = [g["statutory_wage_base"] for g in gaps]
rates     = [g.get("sui_tax_rate", 0.025) * 100 for g in gaps]
total_dmv = sum(g["aggregate_gap"] for g in gaps)

colors = [STATE_COLORS.get(s, GOLD) for s in states]

# ── Figure 05: Per-employee gap ────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
apply_dark_style(ax,
    "SUI Employer Contribution Gap: Per-Employee Loss (2026)",
    ylabel="Per-Employee Underpayment ($/year)")

bars = ax.bar(states, per_emp, color=colors, edgecolor=GRID, linewidth=0.8, width=0.5)
ax.axhline(0, color=GRID, linewidth=0.5)

for bar, val, rate in zip(bars, per_emp, rates):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2.5,
            f"${val:.2f}", ha="center", va="bottom",
            fontsize=11, fontweight="bold", color=FG, fontfamily="monospace")
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
            f"({rate:.1f}% rate)", ha="center", va="center",
            fontsize=8, color=BG, fontweight="bold")

ax.text(0.97, 0.97, f"Total DMV: ${total_dmv/1e6:.1f}M/year",
        transform=ax.transAxes, ha="right", va="top", fontsize=10,
        color=GOLD, fontweight="bold", fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor=BG2, edgecolor=GOLD, alpha=0.9))

plt.tight_layout()
plt.savefig(output_dir / "05_employer_per_employee_gap.png", dpi=150,
            bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ Saved figures/05_employer_per_employee_gap.png")

# ── Figure 06: Aggregate gap ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
apply_dark_style(ax,
    "SUI Trust Fund Shortfall by State (2026)",
    ylabel="Annual Shortfall ($ Millions)")

bars = ax.bar(states, aggregate, color=colors, edgecolor=GRID, linewidth=0.8, width=0.5)

for bar, val in zip(bars, aggregate):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 4,
            f"${val:.1f}M", ha="center", va="bottom",
            fontsize=11, fontweight="bold", color=FG, fontfamily="monospace")

ax.text(0.97, 0.97, f"Total: ${sum(aggregate):.1f}M/year",
        transform=ax.transAxes, ha="right", va="top", fontsize=11,
        color=GOLD, fontweight="bold", fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor=BG2, edgecolor=GOLD, alpha=0.9))

plt.tight_layout()
plt.savefig(output_dir / "06_employer_aggregate_gap.png", dpi=150,
            bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ Saved figures/06_employer_aggregate_gap.png")

# ── Figure 07: Statutory vs Expected wage base ────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
apply_dark_style(ax,
    "SUI Taxable Wage Base: Statutory vs. Expected (2026)",
    ylabel="Taxable Wage Base ($)")

x = range(len(states))
width = 0.38
bars1 = ax.bar([i - width / 2 for i in x], statutory, width,
               label="Statutory (Frozen)", color=BLUE, edgecolor=GRID, linewidth=0.8)
bars2 = ax.bar([i + width / 2 for i in x], expected, width,
               label="Expected (2010 Wage Ratio)", color=CRIMSON, edgecolor=GRID, linewidth=0.8)

ax.set_xticks(list(x))
ax.set_xticklabels(states, color=FG, fontsize=11)

for bar, val in zip(bars1, statutory):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 150,
            f"${val:,.0f}", ha="center", va="bottom", fontsize=9, color=BLUE,
            fontfamily="monospace")
for bar, val in zip(bars2, expected):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 150,
            f"${val:,.0f}", ha="center", va="bottom", fontsize=9, color=CRIMSON,
            fontfamily="monospace")

legend = ax.legend(facecolor=BG2, edgecolor=GRID, labelcolor=FG, fontsize=9)

plt.tight_layout()
plt.savefig(output_dir / "07_statutory_vs_expected_wage_base.png", dpi=150,
            bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ Saved figures/07_statutory_vs_expected_wage_base.png")

print(f"\n✅ All 3 employer gap charts regenerated")
