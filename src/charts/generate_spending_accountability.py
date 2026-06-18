#!/usr/bin/env python3
"""Figure 10 — Spending Accountability Scatter.

Employer campaign money (FEC 2024 cycle) vs federal UI investment
(USASpending.gov CFDA 17.225) per lawmaker's state.

Migrated from root-level generate_spending_accountability.py to src/charts/ package.
Run: python -m src.charts.generate_spending_accountability
Output: figures/10_spending_accountability.png
"""

import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src import POLITICAL, FIGURES

BG, FG, MUT = "#121212", "#e8e8e8", "#888888"
GREEN, CRIMSON, GOLD = "#00FF41", "#DC143C", "#D4AF37"


def load_fec_profiles():
      path = POLITICAL / "fec_funding_profiles.json"
      with open(path) as f:
                data = json.load(f)
            return data.get("data", data) if isinstance(data, dict) else data


# Federal UI grants per state ($ millions, USASpending CFDA 17.225, approx 2024 cycle)
# Source: generate_context_figure.py USA_SPENDING["2026"] values
FED_UI_SPENDING_M = {
      "MD": 78,
      "VA": 69,
      "DC": 38,
}

STATE_ABBR = {
      "Maryland": "MD",
      "Virginia": "VA",
      "District of Columbia": "DC",
}


def main():
      profiles = load_fec_profiles()

    # Build scatter data: x = business contributions ($), y = fed UI spending ($M)
    names, x_vals, y_vals, states = [], [], [], []
    for p in profiles:
              state = p.get("state", "")
              abbr = STATE_ABBR.get(state, state[:2].upper())
              if abbr not in FED_UI_SPENDING_M:
                            continue
                        biz = p.get("business_contributions", 0) or 0
        fed_ui = FED_UI_SPENDING_M[abbr]
        names.append(p.get("name", "").split()[-1])  # last name only
        x_vals.append(biz / 1e6)   # convert to $M
        y_vals.append(fed_ui)
        states.append(abbr)

    fig, ax = plt.subplots(figsize=(10, 7), dpi=130)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=MUT)
    for s in ("top", "right"):
              ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
              ax.spines[s].set_color("#2a2a2a")

    scatter = ax.scatter(x_vals, y_vals, s=120, c=CRIMSON, alpha=0.85, zorder=3)

    for name, x, y in zip(names, x_vals, y_vals):
              ax.annotate(name, (x, y), textcoords="offset points", xytext=(8, 4),
                                              color=FG, fontsize=9, family="monospace")

    ax.set_xlabel("Business Contributions ($ millions, FEC 2024 cycle)",
                                    color=MUT, family="monospace")
    ax.set_ylabel("State Federal UI Grant ($M, CFDA 17.225)",
                                    color=MUT, family="monospace")
    ax.set_title("EMPLOYER MONEY vs. FEDERAL UI INVESTMENT",
                                  color=GREEN, fontsize=14, fontweight="bold",
                                  family="monospace", loc="left", pad=16)
    ax.text(0, 1.03,
                        "Each point = one lawmaker — scatter shows who collects from employers "
                        "vs. what their state gets back in UI funding",
                        transform=ax.transAxes, color=MUT, fontsize=10, family="monospace")
    ax.text(0, -0.13,
                        "Source: FEC API v1 (cycle=2024) × USASpending.gov CFDA 17.225 — The Data Vigilante",
                        transform=ax.transAxes, color="#555555", fontsize=8, family="monospace")

    plt.tight_layout()
    out = FIGURES / "10_spending_accountability.png"
    plt.savefig(out, facecolor=BG, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
      main()
