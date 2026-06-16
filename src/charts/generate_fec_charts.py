import json
from src import DATA, POLITICAL, FIGURES  # repo-root-anchored paths
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
ORANGE  = "#F39C12"

STATE_COLORS = {"MD": BLUE, "VA": GREEN, "DC": GOLD}

def apply_dark_style(ax, title, xlabel=None, ylabel=None):
    ax.set_facecolor(BG2)
    ax.figure.patch.set_facecolor(BG)
    ax.set_title(title, color=LIME, fontsize=12, fontweight="bold",
                 fontfamily="monospace", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, color=MUTED, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, color=MUTED, fontsize=10)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.spines[:].set_color(GRID)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)
    ax.grid(color=GRID, linewidth=0.5, linestyle="--", alpha=0.6)

output_dir = FIGURES
output_dir.mkdir(exist_ok=True)

with open(POLITICAL / "fec_funding_profiles.json") as f:
    raw = json.load(f)

# Handle _metadata-wrapped format
profiles = raw.get("data", raw) if isinstance(raw, dict) else raw

# Verify cycle
bad = [p["name"] for p in profiles if p.get("cycle") != 2024]
if bad:
    print(f"⚠️  Non-2024 cycle data detected for: {bad}. Charts may include multi-cycle totals.")

# ── Figure 11: Total Receipts (horizontal bar, sorted) ────────────────────────
profiles_sorted = sorted(profiles, key=lambda p: p["total_receipts"])

fig, ax = plt.subplots(figsize=(11, 6))
apply_dark_style(ax,
    "Total Campaign Receipts — UI Committee Members (FEC, 2024 Cycle)",
    xlabel="Total Receipts ($)")

names  = [f"{p['name']}  ({p['state']})" for p in profiles_sorted]
totals = [p["total_receipts"] for p in profiles_sorted]
bar_colors = [STATE_COLORS.get(p["state"], GOLD) for p in profiles_sorted]

bars = ax.barh(range(len(profiles_sorted)), totals, color=bar_colors,
               edgecolor=GRID, linewidth=0.6, height=0.6)

ax.set_yticks(range(len(profiles_sorted)))
ax.set_yticklabels(names, color=FG, fontsize=9, fontfamily="monospace")
ax.xaxis.set_major_formatter(
    matplotlib.ticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M" if x >= 1e6 else f"${x/1e3:.0f}K")
)

for bar, val in zip(bars, totals):
    label = f"${val/1e6:.1f}M" if val >= 1e6 else f"${val/1e3:.0f}K"
    ax.text(bar.get_width() + max(totals) * 0.01, bar.get_y() + bar.get_height() / 2,
            label, va="center", ha="left", fontsize=9, color=FG,
            fontfamily="monospace", fontweight="bold")

legend_patches = [
    mpatches.Patch(color=BLUE,  label="Maryland"),
    mpatches.Patch(color=GREEN, label="Virginia"),
    mpatches.Patch(color=GOLD,  label="DC"),
]
legend = ax.legend(handles=legend_patches, facecolor=BG2, edgecolor=GRID,
                   labelcolor=FG, fontsize=9, loc="lower right")

ax.set_xlim(0, max(totals) * 1.18)
plt.tight_layout()
plt.savefig(output_dir / "11_fec_total_receipts.png", dpi=150,
            bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ Saved figures/11_fec_total_receipts.png")

# ── Figure 12: Business vs. Labor (stacked bar) ────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 6))
apply_dark_style(ax,
    "Business vs. Labor Contributions — UI Committee Members (FEC Schedule A, ≥$500)",
    ylabel="Itemized Contributions ($)")

x = range(len(profiles))
width = 0.55
biz    = [p.get("business_contributions", 0) for p in profiles]
labor  = [p.get("labor_contributions", 0) for p in profiles]
other  = [p.get("other_contributions", 0) for p in profiles]

ax.bar(x, biz,   width, label="Business / Industry", color=CRIMSON,
       edgecolor=GRID, linewidth=0.6)
ax.bar(x, labor, width, bottom=biz, label="Labor Unions", color=BLUE,
       edgecolor=GRID, linewidth=0.6)
ax.bar(x, other, width, bottom=[b + l for b, l in zip(biz, labor)],
       label="Other / PAC", color=GOLD, edgecolor=GRID, linewidth=0.6, alpha=0.85)

xlabels = [f"{p['name']}\n({p['state']})" for p in profiles]
ax.set_xticks(list(x))
ax.set_xticklabels(xlabels, color=FG, fontsize=8, fontfamily="monospace", rotation=10, ha="right")
ax.yaxis.set_major_formatter(
    matplotlib.ticker.FuncFormatter(lambda y, _: f"${y/1e3:.0f}K" if y > 0 else "$0")
)

legend = ax.legend(facecolor=BG2, edgecolor=GRID, labelcolor=FG, fontsize=9)

# Annotate total itemized above each bar
for i, p in enumerate(profiles):
    total_itemized = p.get("business_contributions", 0) + p.get("labor_contributions", 0) + p.get("other_contributions", 0)
    if total_itemized > 0:
        ax.text(i, total_itemized + max([b+l+o for b, l, o in zip(biz, labor, other)]) * 0.02,
                f"${total_itemized/1e3:.0f}K", ha="center", va="bottom",
                fontsize=8, color=MUTED, fontfamily="monospace")

plt.tight_layout()
plt.savefig(output_dir / "12_fec_business_vs_labor.png", dpi=150,
            bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ Saved figures/12_fec_business_vs_labor.png")

# ── Figure 13: Contribution source mix (% stacked horizontal) ─────────────────
fig, ax = plt.subplots(figsize=(11, 6))
apply_dark_style(ax,
    "Contribution Source Mix — UI Committee Members (% of Itemized, FEC 2024)",
    xlabel="Percentage of Itemized Contributions")

for i, p in enumerate(profiles):
    total = (p.get("individual_contributions", 0) +
             p.get("pac_contributions", 0) +
             p.get("business_contributions", 0))
    if total > 0:
        indiv_pct = p.get("individual_contributions", 0) / total * 100
        pac_pct   = p.get("pac_contributions", 0) / total * 100
        biz_pct   = p.get("business_contributions", 0) / total * 100
    else:
        indiv_pct = pac_pct = biz_pct = 0

    ax.barh(i, indiv_pct, color=GREEN,  alpha=0.9, height=0.6,
            label="Individual" if i == 0 else "", edgecolor=GRID, linewidth=0.4)
    ax.barh(i, pac_pct,   left=indiv_pct, color=ORANGE, alpha=0.9, height=0.6,
            label="PAC / Committee" if i == 0 else "", edgecolor=GRID, linewidth=0.4)
    ax.barh(i, biz_pct,   left=indiv_pct + pac_pct, color=CRIMSON, alpha=0.9, height=0.6,
            label="Business / Industry" if i == 0 else "", edgecolor=GRID, linewidth=0.4)

names_13 = [f"{p['name']}  ({p['state']})" for p in profiles]
ax.set_yticks(range(len(profiles)))
ax.set_yticklabels(names_13, color=FG, fontsize=9, fontfamily="monospace")
ax.set_xlim(0, 110)
ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.0f%%"))

legend = ax.legend(facecolor=BG2, edgecolor=GRID, labelcolor=FG,
                   fontsize=9, loc="lower right")

plt.tight_layout()
plt.savefig(output_dir / "13_fec_contribution_mix.png", dpi=150,
            bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ Saved figures/13_fec_contribution_mix.png")

print(f"\n✅ All 3 FEC charts regenerated from {len(profiles)} member profiles")
