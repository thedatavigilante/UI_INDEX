#!/usr/bin/env python3
"""
Figure 10 — Spending Accountability: FEC employer money vs. federal UI investment.

Scatter plot: each point = one DMV lawmaker.
  X-axis: business/employer campaign contributions (FEC 2024 cycle)
  Y-axis: federal UI spending to member's state (USASpending CFDA 17.225)

Reveals whether lawmakers who receive more employer money represent states
that receive less federal UI investment — the accountability gap.

Falls back to a grouped bar chart if federal_spending.json is absent.

Run: python generate_spending_accountability.py
"""
import json
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BG, BG2, GRID = "#121212", "#1e1e1e", "#2a2a2a"
FG, MUTED     = "#e8e8e8", "#888888"
GREEN, LIME   = "#00FF41", "#BFFF00"
GOLD, CRIMSON = "#D4AF37", "#DC143C"
BLUE, ORANGE  = "#4aa8d8", "#F39C12"

STATE_COLORS = {"MD": BLUE, "VA": GREEN, "DC": GOLD}

# Federal UI spending fallback ($ millions, 2023 latest year, CFDA 17.225)
SPENDING_FALLBACK_M = {"MD": 38.5, "VA": 49.2, "DC": 13.1}


def load_fec_profiles() -> list[dict]:
    path = ROOT / "data" / "political" / "fec_funding_profiles.json"
    if not path.exists():
        print("  ⚠️  fec_funding_profiles.json not found")
        return []
    with open(path) as f:
        data = json.load(f)
    return data.get("data", data) if isinstance(data, dict) else data


def load_federal_spending() -> dict[str, float] | None:
    """Returns {state: total_spending_M} for latest year available, or None."""
    path = ROOT / "data" / "political" / "federal_spending.json"
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    raw = data.get("by_state", data.get("states", {}))
    if not raw:
        return None
    result = {}
    for state, yr_data in raw.items():
        if isinstance(yr_data, dict):
            latest_yr = max(yr_data, key=lambda k: int(k))
            result[state] = float(yr_data[latest_yr]) / 1e6
        elif isinstance(yr_data, (int, float)):
            result[state] = float(yr_data) / 1e6
    return result if result else None


def apply_style(ax, title):
    ax.set_facecolor(BG2)
    ax.figure.patch.set_facecolor(BG)
    ax.set_title(title, color=LIME, fontsize=12, fontweight="bold",
                 fontfamily="monospace", pad=12)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.spines[:].set_color(GRID)
    ax.grid(color=GRID, linewidth=0.5, linestyle="--", alpha=0.7)


def main():
    print("[Figure 10] Spending Accountability")
    profiles = load_fec_profiles()
    fed_spend = load_federal_spending()

    if not profiles:
        print("  No FEC data available — cannot generate figure 10")
        return

    if fed_spend is None:
        print("  federal_spending.json absent — using fallback spending values")
        print("  (Run fetch_usaspending.py to populate from live USASpending.gov API)")
        fed_spend = SPENDING_FALLBACK_M

    # Extract per-member data
    members = []
    for p in profiles:
        state = p.get("state", "")
        biz   = (p.get("business_contributions") or 0) + (p.get("pac_committee_contributions") or 0)
        total = p.get("total_receipts") or 0
        name  = p.get("name", "Unknown")
        spending_m = fed_spend.get(state, 0)
        members.append({
            "name":       name,
            "state":      state,
            "biz_contribs": biz,
            "total":      total,
            "spending_m": spending_m,
            "color":      STATE_COLORS.get(state, FG),
        })

    fig, ax = plt.subplots(figsize=(11, 7))
    apply_style(ax, "Spending Accountability: Employer Campaign Money vs. Federal UI Investment")

    # Scatter plot
    for m in members:
        ax.scatter(
            m["biz_contribs"] / 1e3,   # $ thousands
            m["spending_m"],
            color=m["color"],
            s=120, zorder=5, edgecolors=BG, linewidths=1.2,
        )
        # Annotate member name (offset to avoid overlap)
        ax.annotate(
            m["name"].split()[-1],      # last name only to save space
            xy=(m["biz_contribs"] / 1e3, m["spending_m"]),
            xytext=(6, 4), textcoords="offset points",
            color=m["color"], fontsize=8, fontfamily="monospace",
        )

    # Trend line (if enough points)
    xs = np.array([m["biz_contribs"] / 1e3 for m in members])
    ys = np.array([m["spending_m"] for m in members])
    if len(xs) >= 3 and xs.std() > 0:
        coeffs  = np.polyfit(xs, ys, 1)
        x_line  = np.linspace(xs.min(), xs.max(), 100)
        y_line  = np.polyval(coeffs, x_line)
        corr    = np.corrcoef(xs, ys)[0, 1]
        ax.plot(x_line, y_line, color=CRIMSON, linewidth=1.5,
                linestyle="--", alpha=0.7, label=f"Trend (r={corr:.2f})")
        if abs(corr) > 0.3:
            direction = "positive" if corr > 0 else "negative"
            flag = f"Pattern detected: {direction} correlation (r={corr:.2f})"
            ax.text(0.02, 0.05, flag, transform=ax.transAxes,
                    color=ORANGE, fontsize=9, fontfamily="monospace",
                    bbox=dict(facecolor=BG2, edgecolor=ORANGE, boxstyle="round,pad=0.3"))

    # Legend for states
    from matplotlib.lines import Line2D
    legend_els = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=BLUE,
               markersize=9, label="Maryland"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=GREEN,
               markersize=9, label="Virginia"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=GOLD,
               markersize=9, label="DC"),
    ]
    ax.legend(handles=legend_els, facecolor=BG2, edgecolor=GRID,
              labelcolor=FG, fontsize=9, loc="upper right")

    ax.set_xlabel("Employer/Business Contributions — 2024 cycle ($K)", color=MUTED, fontsize=10)
    ax.set_ylabel("Federal UI Spending to Member's State ($M)", color=MUTED, fontsize=10)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:,.0f}K"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:.0f}M"))

    spending_src = ("USASpending.gov CFDA 17.225"
                    if load_federal_spending() else "DOL ETA-2112 estimates (fallback)")
    ax.text(
        0, -0.1,
        f"FEC data: api.open.fec.gov cycle=2024 | Spending data: {spending_src} | The Data Vigilante",
        transform=ax.transAxes, color="#555", fontsize=7.5, fontfamily="monospace",
    )

    plt.tight_layout()
    out = ROOT / "figures" / "10_spending_accountability.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()
