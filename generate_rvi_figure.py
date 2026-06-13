#!/usr/bin/env python3
"""Figure 08 — The Real Value Index (inflation-adjusted frozen UI benefits).
Additive: brand-matched to figures 01-07. Method: real = nominal / (CPI2026/CPIbase),
BLS CPI-U annual averages; 2014->2026 anchor = 40.67% (in2013dollars/BLS)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BG, FG, MUT = "#121212", "#e8e8e8", "#888888"
GREEN, LIME, GOLD, CRIMSON = "#00FF41", "#BFFF00", "#D4AF37", "#DC143C"

states = ["Maryland\nfrozen 2014  -29%", "Virginia\nfrozen 2008  -35%", "DC\nsince 2018  -25%"]
nominal = [430, 378, 444]
real    = [306, 244, 335]

x = np.arange(len(states)); w = 0.38
fig, ax = plt.subplots(figsize=(10, 6), dpi=140)
fig.patch.set_facecolor(BG); ax.set_facecolor(BG)

b1 = ax.bar(x - w/2, nominal, w, label="On paper (nominal)", color=GOLD)
b2 = ax.bar(x + w/2, real,    w, label="Real value (2026 dollars)", color=CRIMSON)

for bars in (b1, b2):
    for r in bars:
        ax.text(r.get_x()+r.get_width()/2, r.get_height()+6, f"${int(r.get_height())}",
                ha="center", va="bottom", color=FG, fontsize=12, fontweight="bold",
                family="monospace")

ax.set_title("THE REAL VALUE INDEX", color=GREEN, fontsize=18, fontweight="bold",
             family="monospace", loc="left", pad=18)
ax.text(0, 1.045, "What your frozen unemployment check is actually worth in 2026 dollars",
        transform=ax.transAxes, color=MUT, fontsize=11, family="monospace")
ax.set_xticks(x); ax.set_xticklabels(states, color=FG, fontsize=11, family="monospace")
ax.set_ylim(0, 500); ax.set_ylabel("Max weekly benefit ($)", color=MUT, family="monospace")
ax.tick_params(colors=MUT)
for s in ("top", "right"): ax.spines[s].set_visible(False)
for s in ("left", "bottom"): ax.spines[s].set_color("#2a2a2a")
leg = ax.legend(facecolor=BG, edgecolor="#2a2a2a", labelcolor=FG, fontsize=10)
ax.text(0, -0.16, "Method: nominal / (CPI2026/CPIbase), BLS CPI-U annual avgs - 2014->2026 anchor 40.67% (in2013dollars/BLS)  -  The Data Vigilante",
        transform=ax.transAxes, color="#555555", fontsize=8, family="monospace")
plt.tight_layout()
plt.savefig("figures/08_real_value_index.png", facecolor=BG, bbox_inches="tight")
print("wrote figures/08_real_value_index.png")
