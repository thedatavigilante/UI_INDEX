"""
Fig 5.5 — Scatter: Constituent Median Income vs. Per-Employee Trust Fund Gap
Fig 5.6 — Diverging Bar: Lawmaker Pay Change vs. UI Benefit Change (2014-2026)
"""
import json
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

STATE_COLORS = {"MD": BLUE, "VA": GREEN, "DC": GOLD}
PARTY_COLORS = {"Republican": CRIMSON, "Democratic": BLUE}

output_dir = Path("figures")
output_dir.mkdir(exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────────────────
try:
    with open("data/political/political_layer_report.json") as f:
        plr = json.load(f)
    members = plr["data"]["ui_members_detail"]
except Exception as e:
    print(f"⚠ Political layer fallback: {e}")
    members = []

try:
    with open("data/political/employer_contribution_gap.json") as f:
        raw_emp = json.load(f)
    emp_gaps = raw_emp.get("data", raw_emp) if isinstance(raw_emp, dict) else raw_emp
    per_emp_gap = {g["state"]: g["per_employee_gap"] for g in emp_gaps}
except Exception as e:
    print(f"⚠ Employer gap fallback: {e}")
    per_emp_gap = {"MD": 87.53, "VA": 64.40, "DC": 132.01}

# ─────────────────────────────────────────────────────────────────────
# FIG 26 — Scatter: Constituent Income vs. Per-Employee Gap
# ─────────────────────────────────────────────────────────────────────
scatter_data = []
for m in members:
    income = m.get("constituent_median_income")
    state  = m.get("state")
    if income and state in per_emp_gap:
        scatter_data.append({
            "name":    m["name"],
            "state":   state,
            "party":   m.get("party", "Unknown"),
            "income":  income,
            "gap":     per_emp_gap[state],
            "chamber": m.get("chamber", "House"),
        })

fig, ax = plt.subplots(figsize=(11, 7))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG2)

# Plot each member
for d in scatter_data:
    col   = STATE_COLORS.get(d["state"], MUTED)
    shape = "D" if d["chamber"] == "Senate" else "o"
    ax.scatter(d["income"] / 1000, d["gap"],
               color=col, s=110, marker=shape,
               edgecolors=BG, linewidths=1.2,
               alpha=0.85, zorder=4)

    # Annotate only notable outliers
    if d["income"] > 140000 or d["income"] < 65000 or d["gap"] > 120:
        ax.annotate(
            f"  {d['name'].split()[-1]}\n  ({d['state']})",
            (d["income"] / 1000, d["gap"]),
            fontsize=7, color=col, fontfamily="monospace",
            xytext=(4, 0), textcoords="offset points",
        )

# State-level gap lines
for state, gap in per_emp_gap.items():
    ax.axhline(gap, color=STATE_COLORS[state], linewidth=0.8,
               linestyle=":", alpha=0.4)
    ax.text(55, gap + 1.5, f"{state}: ${gap:.0f}/worker/yr",
            color=STATE_COLORS[state], fontsize=7.5, fontfamily="monospace")

ax.set_xlabel("Constituent Median Household Income ($K, ACS 2022)", color=MUTED, fontsize=10)
ax.set_ylabel("Per-Employee Trust Fund Gap ($/worker/year, 2026)", color=MUTED, fontsize=10)
ax.tick_params(colors=MUTED, labelsize=9, length=0)
ax.spines[:].set_color(GRID)
ax.grid(color=GRID, linewidth=0.5, linestyle="--", alpha=0.5)

ax.set_title(
    "Constituent Income vs. Per-Employee Trust Fund Gap\n(Each dot = one DMV legislator)",
    color=LIME, fontsize=13, fontweight="bold", fontfamily="monospace", pad=12
)

# Legend
legend_items = [
    mpatches.Patch(color=BLUE,    label="Maryland legislators"),
    mpatches.Patch(color=GREEN,   label="Virginia legislators"),
    mpatches.Patch(color=GOLD,    label="DC legislators"),
    plt.Line2D([0],[0], marker="o", color="w", markerfacecolor=MUTED,
               markersize=8, label="House member"),
    plt.Line2D([0],[0], marker="D", color="w", markerfacecolor=MUTED,
               markersize=8, label="Senator"),
]
ax.legend(handles=legend_items, facecolor=BG2, edgecolor=GRID,
          labelcolor=FG, fontsize=8.5, loc="upper right")

ax.text(0.5, -0.1,
        "Gap = per-employee annual shortfall from frozen taxable wage base (2026). "
        "Income = district median HHI (Census ACS 2022 5-year).\n"
        "Note: Senators use statewide median income. "
        "Source: political_layer_report.json · employer_contribution_gap.json",
        transform=ax.transAxes, ha="center", fontsize=7.5, color=MUTED, fontfamily="monospace")

plt.tight_layout()
plt.savefig(output_dir / "26_constituent_income_scatter.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ Saved figures/26_constituent_income_scatter.png")

# ─────────────────────────────────────────────────────────────────────
# FIG 27 — Diverging Bar: Lawmaker Pay vs. UI Benefit Change (2014–2026)
# ─────────────────────────────────────────────────────────────────────
# Data: from the existing lawmaker table (hardcoded verified values)
LAWMAKERS = [
    # (label, their_pct_change, ui_pct_change, state, ratio_label)
    ("MD General\nAssembly",    +12.5,  0.0,    "MD",      "∞ : 1"),
    ("VA General\nAssembly",    +183.0, +13.8,  "VA",      "13 : 1"),
    ("DC Council\n(auto CPI)",  +15.0,  +23.7,  "DC",      "0.6 : 1"),
    ("U.S. Congress\n(174K)",   0.0,    0.0,    "federal", "—"),
]

fig, ax = plt.subplots(figsize=(11, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG2)

# Two grouped bars per body: [their pay, UI benefit]
x_base = [0, 3, 6, 9]
bar_w  = 0.9

for xi, (label, their_pct, ui_pct, state, ratio) in zip(x_base, LAWMAKERS):
    col = STATE_COLORS.get(state, MUTED)

    # Their pay change bar (left)
    bar_their = ax.bar(xi - bar_w * 0.5, their_pct, width=bar_w,
                       color=LIME, alpha=0.8, edgecolor=GRID, linewidth=0.8)
    # UI benefit bar (right)
    bar_ui = ax.bar(xi + bar_w * 0.5, ui_pct, width=bar_w,
                    color=col, alpha=0.7, edgecolor=GRID, linewidth=0.8)

    # Annotations
    if their_pct != 0:
        ax.text(xi - bar_w * 0.5, their_pct + 2, f"+{their_pct:.0f}%",
                ha="center", va="bottom", fontsize=10, fontweight="bold",
                color=LIME, fontfamily="monospace")
    else:
        ax.text(xi - bar_w * 0.5, 2, "0%", ha="center", va="bottom",
                fontsize=10, color=MUTED, fontfamily="monospace")

    if ui_pct != 0:
        ax.text(xi + bar_w * 0.5, ui_pct + 2, f"+{ui_pct:.0f}%",
                ha="center", va="bottom", fontsize=10, fontweight="bold",
                color=col, fontfamily="monospace")
    else:
        ax.text(xi + bar_w * 0.5, 2, "0%", ha="center", va="bottom",
                fontsize=10, color=CRIMSON, fontfamily="monospace")

    # Ratio label below
    ax.text(xi, -22, f"Ratio: {ratio}", ha="center", va="top",
            fontsize=9, color=col if state != "federal" else MUTED,
            fontfamily="monospace", fontweight="bold")

# Zero baseline
ax.axhline(0, color=GRID, linewidth=1.2)

ax.set_xticks(x_base)
ax.set_xticklabels([l[0] for l in LAWMAKERS], color=FG, fontsize=10,
                   fontfamily="monospace")
ax.set_ylabel("% Change (2014 – 2026)", color=MUTED, fontsize=10)
ax.set_ylim(-30, 210)
ax.tick_params(colors=MUTED, labelsize=9, length=0)
ax.spines[:].set_color(GRID)
ax.grid(color=GRID, linewidth=0.5, linestyle="--", alpha=0.5, axis="y")

ax.set_title(
    "Lawmaker Pay vs. UI Benefit — % Change 2014–2026",
    color=LIME, fontsize=13, fontweight="bold", fontfamily="monospace", pad=12
)

legend_items = [
    mpatches.Patch(color=LIME, alpha=0.8, label="Their salary change (%)"),
    mpatches.Patch(color=BLUE, alpha=0.7, label="UI max benefit change (%) — MD color"),
]
ax.legend(handles=legend_items, facecolor=BG2, edgecolor=GRID,
          labelcolor=FG, fontsize=9, loc="upper right")

ax.text(0.5, -0.14,
        "Sources: MD Compensation Commission 2026 · WSET (VA legislative pay raise 2026) · "
        "DC Code §1-611.09 · CRS RL30064 · State DOL UI benefit schedules",
        transform=ax.transAxes, ha="center", fontsize=7.5, color=MUTED, fontfamily="monospace")

plt.tight_layout()
plt.savefig(output_dir / "27_lawmaker_pay_diverging.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ Saved figures/27_lawmaker_pay_diverging.png")

print("\n✅ Both accountability charts generated.")
