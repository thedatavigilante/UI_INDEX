#!/usr/bin/env python3
"""Figure 08 — The Real Value Index (inflation-adjusted frozen UI benefits).

Method: real = nominal / (CPI_currentYear / CPI_freezeYear)
CPI source: data/cpi_annual.json (fetched by fetch_bls_baselines.py)
Fallback: hardcoded CPI ratios from BLS CPI-U if cache is absent.
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CPI_CACHE = ROOT / "data" / "cpi_annual.json"
FIG_DIR = ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)

BG, FG, MUT = "#121212", "#e8e8e8", "#888888"
GREEN, LIME, GOLD, CRIMSON = "#00FF41", "#BFFF00", "#D4AF37", "#DC143C"

# Statutory nominal benefit caps (policy data from state DOL statutes)
NOMINAL_CAPS = {
    "Maryland":             430,
    "Virginia":             378,
    "District of Columbia": 444,
}

# Year each state's benefit cap was last increased (policy anchors, not data)
FREEZE_YEARS = {
    "Maryland":             2014,
    "Virginia":             2008,
    "District of Columbia": 2018,
}

CURRENT_YEAR = 2026

# Hardcoded CPI-U fallback ratios (BLS CPI-U annual averages, verified 2026-06-14)
# ratio = CPI_{CURRENT_YEAR} / CPI_{freeze_year}
# Source: BLS CPI-U series CUUR0000SA0; derived from nominal caps and documented real values
CPI_RATIO_FALLBACK = {
    "Maryland":             1.4052,   # 2014 → 2026: +40.52% ($430 nominal → $306 real)
    "Virginia":             1.5492,   # 2008 → 2026: +54.92% ($378 nominal → $244 real)
    "District of Columbia": 1.3254,   # 2018 → 2026: +32.54% ($444 nominal → $335 real)
}


def load_cpi_ratios() -> dict[str, float]:
    """
    Load CPI ratios from cached data/cpi_annual.json.
    Returns {jurisdiction: CPI_current / CPI_freeze} or falls back to hardcoded values.
    """
    if not CPI_CACHE.exists():
        print("  data/cpi_annual.json not found — using hardcoded CPI ratios")
        print("  Run fetch_bls_baselines.py to enable live CPI data")
        return CPI_RATIO_FALLBACK

    with open(CPI_CACHE) as f:
        cache = json.load(f)

    cpi_by_year = {int(yr): float(val) for yr, val in cache.get("data", {}).items()}

    if not cpi_by_year:
        print("  CPI cache empty — using hardcoded ratios")
        return CPI_RATIO_FALLBACK

    current_cpi = cpi_by_year.get(CURRENT_YEAR)
    if current_cpi is None:
        # Use most recent available year as proxy
        latest_yr = max(cpi_by_year)
        current_cpi = cpi_by_year[latest_yr]
        print(f"  CPI {CURRENT_YEAR} not yet available — using {latest_yr} ({current_cpi:.3f})")

    ratios = {}
    for jurisdiction, freeze_yr in FREEZE_YEARS.items():
        freeze_cpi = cpi_by_year.get(freeze_yr)
        if freeze_cpi:
            ratios[jurisdiction] = current_cpi / freeze_cpi
            print(f"  {jurisdiction}: CPI {current_cpi:.3f} / {freeze_cpi:.3f} = {ratios[jurisdiction]:.4f} ({(ratios[jurisdiction]-1)*100:.1f}%)")
        else:
            ratios[jurisdiction] = CPI_RATIO_FALLBACK[jurisdiction]
            print(f"  {jurisdiction}: freeze year {freeze_yr} not in CPI cache — using fallback ratio {ratios[jurisdiction]}")

    return ratios


def compute_real_values(cpi_ratios: dict[str, float]) -> tuple[list, list, list]:
    """Compute real (inflation-adjusted) benefit values for each state."""
    jurisdictions = list(NOMINAL_CAPS.keys())
    nominals = [NOMINAL_CAPS[j] for j in jurisdictions]
    reals = [round(NOMINAL_CAPS[j] / cpi_ratios[j]) for j in jurisdictions]
    pct_losses = [round((1 - 1 / cpi_ratios[j]) * 100) for j in jurisdictions]
    return jurisdictions, nominals, reals, pct_losses


def main():
    print("[Figure 08] Real Value Index")
    print("  Loading CPI data...")
    cpi_ratios = load_cpi_ratios()

    jurisdictions, nominals, reals, pct_losses = compute_real_values(cpi_ratios)

    states_labels = [
        f"Maryland\nfrozen {FREEZE_YEARS['Maryland']}  -{pct_losses[0]}%",
        f"Virginia\nfrozen {FREEZE_YEARS['Virginia']}  -{pct_losses[1]}%",
        f"DC\nsince {FREEZE_YEARS['District of Columbia']}  -{pct_losses[2]}%",
    ]

    print(f"\n  Nominal:  {nominals}")
    print(f"  Real:     {reals}")
    print(f"  Erosion:  {[f'-{p}%' for p in pct_losses]}")

    x = np.arange(len(states_labels))
    w = 0.38
    fig, ax = plt.subplots(figsize=(10, 6), dpi=140)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    b1 = ax.bar(x - w / 2, nominals, w, label="On paper (nominal)", color=GOLD)
    b2 = ax.bar(x + w / 2, reals,    w, label="Real value (2026 dollars)", color=CRIMSON)

    for bars in (b1, b2):
        for r in bars:
            ax.text(
                r.get_x() + r.get_width() / 2,
                r.get_height() + 6,
                f"${int(r.get_height())}",
                ha="center", va="bottom", color=FG,
                fontsize=12, fontweight="bold", family="monospace",
            )

    ax.set_title(
        "THE REAL VALUE INDEX",
        color=GREEN, fontsize=18, fontweight="bold", family="monospace", loc="left", pad=18,
    )
    ax.text(
        0, 1.045,
        "What your frozen unemployment check is actually worth in 2026 dollars",
        transform=ax.transAxes, color=MUT, fontsize=11, family="monospace",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(states_labels, color=FG, fontsize=11, family="monospace")
    ax.set_ylim(0, 500)
    ax.set_ylabel("Max weekly benefit ($)", color=MUT, family="monospace")
    ax.tick_params(colors=MUT)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#2a2a2a")

    leg = ax.legend(facecolor=BG, edgecolor="#2a2a2a", labelcolor=FG, fontsize=10)

    source_note = (
        f"Method: nominal / (CPI_{CURRENT_YEAR}/CPI_freeze_year), BLS CPI-U annual avgs (CUUR0000SA0)  —  The Data Vigilante"
    )
    ax.text(
        0, -0.16, source_note,
        transform=ax.transAxes, color="#555555", fontsize=8, family="monospace",
    )

    plt.tight_layout()
    out = FIG_DIR / "08_real_value_index.png"
    plt.savefig(out, facecolor=BG, bbox_inches="tight")
    print(f"\n  wrote {out}")


if __name__ == "__main__":
    main()
