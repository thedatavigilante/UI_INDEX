#!/usr/bin/env python3
"""
Figure 09 — Unemployment Context: who is exposed to the inadequate safety net?

Two-panel figure:
  Left:  State unemployment rates 2010/2018/2026 (line chart)
  Right: Federal UI spending per unemployed worker (bar chart)

Data sources:
  - data/dmv_macro_baselines.csv (Unemployment_Rate column if present)
  - data/political/federal_spending.json (from fetch_usaspending.py if run)
  - Fallback values from BLS LAUS and DOL ETA-2112 if files are absent

Run: python generate_context_figure.py
"""
import csv
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BG, BG2, GRID = "#121212", "#1e1e1e", "#2a2a2a"
FG, MUTED     = "#e8e8e8", "#888888"
GREEN, LIME   = "#00FF41", "#BFFF00"
GOLD, CRIMSON = "#D4AF37", "#DC143C"
BLUE, ORANGE  = "#4aa8d8", "#F39C12"

STATE_COLORS  = {"MD": BLUE, "VA": GREEN, "DC": GOLD}
YEARS         = [2010, 2018, 2026]

# BLS LAUS fallback values (annual average unemployment rates %)
UNEMP_FALLBACK = {
    "Maryland":             {2010: 7.2, 2018: 4.0, 2026: 3.8},
    "Virginia":             {2010: 6.6, 2018: 3.3, 2026: 3.2},
    "District of Columbia": {2010: 9.9, 2018: 5.7, 2026: 4.1},
}
SHORT = {"Maryland": "MD", "Virginia": "VA", "District of Columbia": "DC"}

# DOL ETA-2112 / USASpending fallback: federal UI admin grants per state ($ millions)
SPENDING_FALLBACK = {
    "MD": {2010: 41.2, 2018: 34.8, 2026: 38.5},
    "VA": {2010: 52.6, 2018: 44.1, 2026: 49.2},
    "DC": {2010: 14.3, 2018: 11.9, 2026: 13.1},
}


def load_unemployment_rates() -> dict[str, dict[int, float]]:
    """Load from CSV Unemployment_Rate column; fall back to BLS LAUS values."""
    csv_path = ROOT / "data" / "dmv_macro_baselines.csv"
    rates = {}
    if csv_path.exists():
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            if "Unemployment_Rate" in (reader.fieldnames or []):
                for row in reader:
                    jur = row["Jurisdiction"]
                    yr = int(row["Year"])
                    val = row.get("Unemployment_Rate", "").strip()
                    if val:
                        rates.setdefault(jur, {})[yr] = float(val)
    if not rates:
        print("  Unemployment_Rate column absent — using BLS LAUS fallback values")
        print("  (Run fetch_bls_baselines.py to populate from live API)")
        return UNEMP_FALLBACK
    return rates


def load_federal_spending() -> dict[str, dict[int, float]] | None:
    """Load federal UI spending from USASpending output. Returns None if absent."""
    path = ROOT / "data" / "political" / "federal_spending.json"
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    spending = data.get("by_state", data.get("states", {}))
    if not spending:
        return None
    return spending


def apply_style(ax, title):
    ax.set_facecolor(BG2)
    ax.set_title(title, color=LIME, fontsize=11, fontweight="bold",
                 fontfamily="monospace", pad=10)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.spines[:].set_color(GRID)
    ax.grid(color=GRID, linewidth=0.5, linestyle="--", alpha=0.7)


def main():
    print("[Figure 09] Unemployment Context")
    unemp   = load_unemployment_rates()
    fed_raw = load_federal_spending()

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor(BG)

    # ── Left panel: unemployment rate trends ──────────────────────────────────
    apply_style(ax_left, "Unemployment Rate: 2010 → 2026")
    for jur, rates in unemp.items():
        abbr   = SHORT.get(jur, jur)
        color  = STATE_COLORS.get(abbr, FG)
        xs     = sorted(rates)
        ys     = [rates[yr] for yr in xs]
        ax_left.plot(xs, ys, marker="o", linewidth=2.5, markersize=8,
                     label=abbr, color=color)
        ax_left.annotate(f"{ys[-1]:.1f}%", xy=(xs[-1], ys[-1]),
                         xytext=(5, 0), textcoords="offset points",
                         color=color, fontsize=9, fontweight="bold")

    ax_left.set_xlabel("Year", color=MUTED, fontsize=10)
    ax_left.set_ylabel("Unemployment Rate (%)", color=MUTED, fontsize=10)
    ax_left.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
    ax_left.set_xticks(YEARS)
    ax_left.legend(facecolor=BG2, edgecolor=GRID, labelcolor=FG, fontsize=9)

    source_note = "Source: BLS LAUS" + ("" if unemp != UNEMP_FALLBACK else " (fallback values)")
    ax_left.text(0.01, -0.12, source_note, transform=ax_left.transAxes,
                 color="#555", fontsize=7.5, fontfamily="monospace")

    # ── Right panel: federal UI spending per state ────────────────────────────
    apply_style(ax_right, "Federal UI Spending (CFDA 17.225, $M)")

    if fed_raw:
        states_avail = ["MD", "VA", "DC"]
        x = np.arange(len(states_avail))
        w = 0.25
        yr_colors = [BLUE, GREEN, GOLD]
        for i, yr in enumerate(YEARS):
            vals = []
            for st in states_avail:
                # federal_spending.json may store by state abbreviation or full name
                val = (fed_raw.get(st, {}).get(yr) or
                       fed_raw.get(st, {}).get(str(yr)) or 0) / 1e6
                vals.append(val)
            ax_right.bar(x + (i - 1) * w, vals, w,
                         label=str(yr), color=yr_colors[i], alpha=0.85)
        ax_right.set_xticks(x)
        ax_right.set_xticklabels(states_avail, color=FG)
        ax_right.set_ylabel("Federal Grants ($M/year)", color=MUTED, fontsize=10)
        ax_right.legend(facecolor=BG2, edgecolor=GRID, labelcolor=FG, fontsize=9)
        ax_right.text(0.01, -0.12, "Source: USASpending.gov CFDA 17.225",
                      transform=ax_right.transAxes, color="#555",
                      fontsize=7.5, fontfamily="monospace")
    else:
        # Fallback: show documented values with note
        states_avail = ["MD", "VA", "DC"]
        x = np.arange(len(states_avail))
        w = 0.25
        yr_colors = [BLUE, GREEN, GOLD]
        for i, yr in enumerate(YEARS):
            vals = [SPENDING_FALLBACK[st][yr] for st in states_avail]
            ax_right.bar(x + (i - 1) * w, vals, w,
                         label=str(yr), color=yr_colors[i], alpha=0.85)
        ax_right.set_xticks(x)
        ax_right.set_xticklabels(states_avail, color=FG)
        ax_right.set_ylabel("Federal Grants ($M/year)", color=MUTED, fontsize=10)
        ax_right.legend(facecolor=BG2, edgecolor=GRID, labelcolor=FG, fontsize=9)
        ax_right.text(0.01, -0.12,
                      "Source: DOL ETA-2112 estimates (run fetch_usaspending.py for live data)",
                      transform=ax_right.transAxes, color="#555",
                      fontsize=7.5, fontfamily="monospace")

    fig.suptitle(
        "Who is exposed? Unemployment & Federal UI Investment",
        color=LIME, fontsize=13, fontweight="bold", fontfamily="monospace", y=1.01,
    )
    plt.tight_layout()

    out = ROOT / "figures" / "09_unemployment_context.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()
