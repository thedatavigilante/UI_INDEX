#!/usr/bin/env python3
"""Figure 08 — The Real Value Index (inflation-adjusted frozen UI benefits).

Additive: brand-matched to figures 01-07.
Method: real = nominal / (CPI2026/CPIbase), BLS CPI-U annual averages;
2014->2026 anchor = 40.67% (in2013dollars/BLS).

Data is driven from UIIndexEngine so chart values stay in sync with the CSV
baselines and test_core_math.py::test_real_value_index regression locks.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src import FIGURES
from src.core_engine import UIIndexEngine

BG, FG, MUT = "#121212", "#e8e8e8", "#888888"
GREEN, LIME, GOLD, CRIMSON = "#00FF41", "#BFFF00", "#D4AF37", "#DC143C"

# CPI-U anchor factors per jurisdiction (BLS, anchor year → 2026)
# Used to compute real = nominal / factor
CPI_FACTORS = {
        "Maryland": 1.4067,           # frozen 2014 → 2026 (+40.67%)
        "Virginia": 1.547,            # frozen 2008 → 2026 (+54.7%)
        "District of Columbia": 1.326, # frozen 2018 → 2026 (+32.6%)
}

FREEZE_LABELS = {
        "Maryland": "frozen 2014 -29%",
        "Virginia": "frozen 2008 -35%",
        "District of Columbia": "since 2018 -25%",
}


def build_rvi_data():
        """Pull nominal WBAs from the engine and compute real values via CPI factors."""
        engine = UIIndexEngine()
        indices_2026 = {
            r["Jurisdiction"]: r
            for r in engine.compute_indices()
            if r["Year"] == 2026
        }

    states_ordered = ["Maryland", "Virginia", "District of Columbia"]
    labels, nominal_vals, real_vals = [], [], []

    for jur in states_ordered:
                if jur not in indices_2026:
                                continue
                            nom = indices_2026[jur]["Max_WBA"]
        factor = CPI_FACTORS[jur]
        real = round(nom / factor)
        labels.append(f"{jur.replace('District of Columbia', 'DC')}\n{FREEZE_LABELS[jur]}")
        nominal_vals.append(nom)
        real_vals.append(real)

    return labels, nominal_vals, real_vals


def main():
        states, nominal, real = build_rvi_data()

    x = np.arange(len(states))
    w = 0.38
    fig, ax = plt.subplots(figsize=(10, 6), dpi=140)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    b1 = ax.bar(x - w / 2, nominal, w, label="On paper (nominal)", color=GOLD)
    b2 = ax.bar(x + w / 2, real, w, label="Real value (2026 dollars)", color=CRIMSON)

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
                "THE REAL VALUE INDEX", color=GREEN, fontsize=18,
                fontweight="bold", family="monospace", loc="left", pad=18,
    )
    ax.text(
                0, 1.045,
                "What your frozen unemployment check is actually worth in 2026 dollars",
                transform=ax.transAxes, color=MUT, fontsize=11, family="monospace",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(states, color=FG, fontsize=11, family="monospace")
    ax.set_ylim(0, 500)
    ax.set_ylabel("Max weekly benefit ($)", color=MUT, family="monospace")
    ax.tick_params(colors=MUT)
    for s in ("top", "right"):
                ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
                ax.spines[s].set_color("#2a2a2a")
    ax.legend(facecolor=BG, edgecolor="#2a2a2a", labelcolor=FG, fontsize=10)
    ax.text(
                0, -0.16,
                "Method: nominal / (CPI2026/CPIbase), BLS CPI-U annual avgs — "
                "2014->2026 anchor 40.67% (in2013dollars/BLS) — The Data Vigilante",
                transform=ax.transAxes, color="#555555", fontsize=8, family="monospace",
    )
    plt.tight_layout()
    plt.savefig(FIGURES / "08_real_value_index.png", facecolor=BG, bbox_inches="tight")
    print("wrote figures/08_real_value_index.png")


if __name__ == "__main__":
        main()
