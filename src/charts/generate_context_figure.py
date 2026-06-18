#!/usr/bin/env python3
"""Figure 09 — Unemployment Context (BLS LAUS rates + USASpending federal UI grants).

Migrated from root-level generate_context_figure.py to src/charts/ package.
Run: python -m src.charts.generate_context_figure
Output: figures/09_unemployment_context.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json

from src import DATA, FIGURES

BG, FG, MUT = "#121212", "#e8e8e8", "#888888"
GREEN, GOLD = "#00FF41", "#D4AF37"

# State unemployment rate baselines (BLS LAUS, annual averages)
# Source: data/dmv_macro_baselines.csv (supplemented by BLS LAUS API)
UNEMPLOYMENT_RATES = {
      "Maryland":               {"2010": 7.5, "2018": 4.1, "2026": 3.2},
      "Virginia":               {"2010": 6.8, "2018": 3.0, "2026": 2.9},
      "District of Columbia":   {"2010": 9.9, "2018": 5.6, "2026": 4.8},
}

# USASpending.gov CFDA 17.225 federal UI grants ($ millions, approximate)
USA_SPENDING = {
      "Maryland":             {"2010": 589, "2018": 91,  "2026": 78},
      "Virginia":             {"2010": 412, "2018": 85,  "2026": 69},
      "District of Columbia": {"2010": 198, "2018": 42,  "2026": 38},
}

YEARS = ["2010", "2018", "2026"]
JURS = list(UNEMPLOYMENT_RATES.keys())
ABBRS = ["MD", "VA", "DC"]
COLORS = [GREEN, GOLD, "#DC143C"]


def main():
      fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=130)
      fig.patch.set_facecolor(BG)
      for ax in (ax1, ax2):
                ax.set_facecolor(BG)
                ax.tick_params(colors=MUT)
                for spine in ("top", "right"):
                              ax.spines[spine].set_visible(False)
                          for spine in ("left", "bottom"):
                                        ax.spines[spine].set_color("#2a2a2a")

            # Panel 1: Unemployment rate trends
            x = range(len(YEARS))
    for jur, abbr, color in zip(JURS, ABBRS, COLORS):
              rates = [UNEMPLOYMENT_RATES[jur][y] for y in YEARS]
              ax1.plot(x, rates, marker="o", color=color, linewidth=2, label=abbr)
              for xi, rate in zip(x, rates):
                            ax1.text(xi, rate + 0.15, f"{rate}%", ha="center", va="bottom",
                                                          color=color, fontsize=9, family="monospace")

          ax1.set_xticks(list(x))
    ax1.set_xticklabels(YEARS, color=FG, family="monospace")
    ax1.set_ylabel("Unemployment Rate (%)", color=MUT, family="monospace")
    ax1.set_title("UNEMPLOYMENT RATE TRENDS (BLS LAUS)",
                                    color=GREEN, fontsize=12, fontweight="bold",
                                    family="monospace", loc="left", pad=12)
    ax1.legend(facecolor=BG, edgecolor="#2a2a2a", labelcolor=FG, fontsize=9)

    # Panel 2: Federal UI spending
    width, offsets = 0.25, [-0.25, 0, 0.25]
    for i, (jur, abbr, color) in enumerate(zip(JURS, ABBRS, COLORS)):
              vals = [USA_SPENDING[jur][y] for y in YEARS]
              xi = [j + offsets[i] for j in range(len(YEARS))]
              bars = ax2.bar(xi, vals, width, color=color, alpha=0.85, label=abbr)
              for bar in bars:
                            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                                                          f"${int(bar.get_height())}M", ha="center", va="bottom",
                                                          color=color, fontsize=7, family="monospace")

          ax2.set_xticks(range(len(YEARS)))
    ax2.set_xticklabels(YEARS, color=FG, family="monospace")
    ax2.set_ylabel("Federal UI Grants ($M, CFDA 17.225)", color=MUT, family="monospace")
    ax2.set_title("FEDERAL UI SPENDING (USASpending.gov)",
                                    color=GOLD, fontsize=12, fontweight="bold",
                                    family="monospace", loc="left", pad=12)
    ax2.legend(facecolor=BG, edgecolor="#2a2a2a", labelcolor=FG, fontsize=9)

    fig.suptitle(
              "Who is exposed and who is funding the net  |  The Data Vigilante",
              color=MUT, fontsize=10, family="monospace", y=0.02
    )
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    out = FIGURES / "09_unemployment_context.png"
    plt.savefig(out, facecolor=BG, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
      main()
