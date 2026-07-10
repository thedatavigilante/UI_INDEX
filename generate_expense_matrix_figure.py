#!/usr/bin/env python3
"""
Generate Figure 15 — Expense Category Matrix: Where the UI Check Runs Out.

Three-panel horizontal stacked bar chart (one panel per jurisdiction).
Each panel shows the weekly MIT Living Wage expense categories stacked
left-to-right, with a vertical line marking the UI maximum benefit.
The chart makes visible the exact point at which the check runs out.

Three-tier fallback:
  1. data/col_bai_results.json (expense_breakdown field)
  2. col_bai_engine direct import
  3. Hardcoded values embedded below

Run: python generate_expense_matrix_figure.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# ── Brand palette ─────────────────────────────────────────────────────────────
BG, BG2, GRID = "#121212", "#1e1e1e", "#2a2a2a"
FG, MUTED     = "#e8e8e8", "#888888"
GREEN, LIME   = "#00FF41", "#BFFF00"
GOLD, CRIMSON = "#D4AF37", "#DC143C"
BLUE, ORANGE  = "#4aa8d8", "#F39C12"

OUT_PATH = ROOT / "figures" / "15_expense_matrix.png"

CATEGORIES = ["housing", "food", "transportation", "healthcare", "childcare", "other"]
CAT_LABELS = ["Housing", "Food", "Transportation", "Healthcare", "Childcare", "Other"]

CAT_COLORS = {
    "housing":        CRIMSON,
    "food":           GOLD,
    "transportation": BLUE,
    "healthcare":     ORANGE,
    "childcare":      LIME,
    "other":          MUTED,
}

JURISDICTIONS = ["District of Columbia", "Maryland", "Virginia"]
SHORT         = {"District of Columbia": "DC", "Maryland": "MD", "Virginia": "VA"}

UI_MAX = {
    "District of Columbia": 444,
    "Maryland":             430,
    "Virginia":             430,
}

# Hardcoded fallback (Tier 3) — 2024 MIT Living Wage expense breakdown, 1 adult
FALLBACK_EXPENSES = {
    "District of Columbia": {
        "housing": 476, "food": 96, "transportation": 139,
        "healthcare": 52, "childcare": 0, "other": 86,
    },
    "Maryland": {
        "housing": 337, "food": 90, "transportation": 127,
        "healthcare": 46, "childcare": 0, "other": 75,
    },
    "Virginia": {
        "housing": 285, "food": 85, "transportation": 130,
        "healthcare": 43, "childcare": 0, "other": 70,
    },
}

FALLBACK_WITH_CHILD = {
    "District of Columbia": {
        "housing": 551, "food": 148, "transportation": 139,
        "healthcare": 105, "childcare": 500, "other": 141,
    },
    "Maryland": {
        "housing": 391, "food": 134, "transportation": 127,
        "healthcare": 95, "childcare": 441, "other": 115,
    },
    "Virginia": {
        "housing": 335, "food": 125, "transportation": 130,
        "healthcare": 90, "childcare": 422, "other": 106,
    },
}


def _load_expenses() -> tuple[dict, dict]:
    """Returns (expenses_no_child, expenses_with_child) for 2026 rows."""
    path = ROOT / "data" / "col_bai_results.json"
    if path.exists():
        try:
            with open(path) as f:
                data = json.load(f)
            # Use summary_2026 (which has the breakdown)
            summary = data.get("summary_2026", {})
            no_child, with_child = {}, {}
            for jur, row in summary.items():
                eb = row.get("expense_breakdown")
                ec = row.get("expense_breakdown_with_child")
                if eb:
                    no_child[jur] = eb
                if ec:
                    with_child[jur] = ec
            if no_child:
                print("  [Tier 1] Loaded expense breakdown from col_bai_results.json")
                return no_child, with_child or FALLBACK_WITH_CHILD
        except (json.JSONDecodeError, OSError):
            pass

    # Tier 2: engine
    try:
        from col_bai_engine import MIT_EXPENSE_BREAKDOWN, MIT_EXPENSE_BREAKDOWN_WITH_CHILD
        print("  [Tier 2] Loaded expense breakdown from col_bai_engine")
        return MIT_EXPENSE_BREAKDOWN, MIT_EXPENSE_BREAKDOWN_WITH_CHILD
    except ImportError:
        pass

    print("  [Tier 3] Using hardcoded fallback expense data")
    return FALLBACK_EXPENSES, FALLBACK_WITH_CHILD


def _style_ax(ax):
    ax.set_facecolor(BG2)
    ax.tick_params(colors=FG, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.grid(True, color=GRID, linewidth=0.5, linestyle="--")
    ax.set_axisbelow(True)


def make_figure(expenses: dict, expenses_child: dict):
    fig, axes = plt.subplots(3, 1, figsize=(13, 9))
    fig.patch.set_facecolor(BG)

    for i, jur in enumerate(JURISDICTIONS):
        ax = axes[i]
        _style_ax(ax)

        exp = expenses.get(jur, FALLBACK_EXPENSES[jur])
        ui = UI_MAX[jur]
        short = SHORT[jur]

        # ── Stacked horizontal bar ────────────────────────────────
        left = 0
        for cat, label, color in zip(CATEGORIES, CAT_LABELS, [CAT_COLORS[c] for c in CATEGORIES]):
            val = exp.get(cat, 0)
            if val == 0:
                continue
            ax.barh(0, val, left=left, height=0.5, color=color, alpha=0.88, label=label)
            # Category value label (only if wide enough)
            if val >= 30:
                ax.text(left + val / 2, 0, f"${val}",
                        ha="center", va="center", fontsize=8.5, color=BG,
                        fontweight="bold")
            left += val

        # ── "1 adult + 1 child" scenario bar (lighter, below) ────
        exp_c = expenses_child.get(jur, FALLBACK_WITH_CHILD[jur])
        left_c = 0
        for cat, color in zip(CATEGORIES, [CAT_COLORS[c] for c in CATEGORIES]):
            val_c = exp_c.get(cat, 0)
            if val_c == 0:
                continue
            ax.barh(-0.65, val_c, left=left_c, height=0.38,
                    color=color, alpha=0.45)
            left_c += val_c

        # ── UI benefit line ───────────────────────────────────────
        ax.axvline(ui, color=GREEN, linewidth=2, linestyle="-", zorder=5)
        ax.text(ui + 6, 0.32, f"UI max\n${ui}/wk", color=GREEN,
                fontsize=8, va="top", fontweight="bold")

        # ── Total survival cost annotation ────────────────────────
        total = sum(exp.values())
        total_c = sum(exp_c.values())
        gap = total - ui
        gap_c = total_c - ui

        ax.text(total + 10, 0, f"Total: ${total}/wk\nGap: −${gap}",
                color=CRIMSON, fontsize=8.5, va="center", fontweight="bold")
        ax.text(total_c + 10, -0.65, f"With child: ${total_c}/wk  (−${gap_c})",
                color=CRIMSON, fontsize=7.5, va="center", alpha=0.75)

        # ── Cumulative drain annotation (DC special callout) ──────
        housing_cost = exp.get("housing", 0)
        after_housing = ui - housing_cost
        if after_housing < 0:
            ax.annotate(
                f"Housing alone (${housing_cost}) exceeds UI check — already −${abs(after_housing)} before food",
                xy=(ui, 0.28), xytext=(ui - 200, 0.55),
                fontsize=7.5, color=CRIMSON,
                arrowprops=dict(arrowstyle="->", color=CRIMSON, lw=1.2),
            )
        else:
            ax.text(ui / 2, -0.32,
                    f"After housing: ${after_housing}/wk left",
                    color=GOLD, fontsize=7.5, ha="center", va="center",
                    style="italic")

        # ── Y-axis labels ─────────────────────────────────────────
        ax.set_yticks([0, -0.65])
        ax.set_yticklabels([f"{short}\n1 adult", f"{short}\n1 adult\n+1 child"],
                           fontsize=8, color=FG)
        ax.set_ylim(-1.05, 0.7)

        # ── X-axis limit ──────────────────────────────────────────
        max_x = max(left, left_c) + 120
        ax.set_xlim(0, max_x)
        ax.set_xlabel("Weekly cost ($)", fontsize=8, color=MUTED)

        # ── Panel title ───────────────────────────────────────────
        ax.set_title(
            f"{short} — {jur}",
            color=FG, fontsize=10, fontweight="bold", loc="left", pad=5
        )

        # ── Source note ───────────────────────────────────────────
        if i == 2:
            ax.text(0, -1.9,
                "Source: MIT Living Wage Calculator 2024 (livingwage.mit.edu) — 1 adult, no children / 1 adult + 1 child, state-level.\n"
                "UI Maximum from DOL/state benefit schedules. Expense categories: housing, food, transportation, healthcare, childcare, other necessities.",
                transform=ax.transAxes, color="#555555", fontsize=7, va="top")

    # ── Legend ────────────────────────────────────────────────────
    legend_handles = [mpatches.Patch(color=CAT_COLORS[c], alpha=0.88, label=l)
                      for c, l in zip(CATEGORIES, CAT_LABELS) if c != "childcare"]
    legend_handles.append(mpatches.Patch(color=LIME, alpha=0.88, label="Childcare"))
    legend_handles.append(plt.Line2D([0], [0], color=GREEN, linewidth=2, label="UI Max Benefit"))
    fig.legend(handles=legend_handles, ncol=7, loc="upper center", bbox_to_anchor=(0.5, 1.0),
               facecolor=BG2, edgecolor=GRID, labelcolor=FG, fontsize=8)

    fig.suptitle(
        "Figure 15 — Where the UI Check Runs Out: Weekly Expense Breakdown vs. Benefit",
        color=GREEN, fontsize=13, fontweight="bold", family="monospace",
        x=0.02, ha="left", y=1.035,
    )

    plt.tight_layout(rect=[0, 0.02, 1, 0.97])
    OUT_PATH.parent.mkdir(exist_ok=True)
    plt.savefig(OUT_PATH, facecolor=BG, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"  Saved: {OUT_PATH}")


def main():
    print("=" * 60)
    print("GENERATE FIGURE 15 — EXPENSE CATEGORY MATRIX")
    print("=" * 60)
    expenses, expenses_child = _load_expenses()
    make_figure(expenses, expenses_child)
    print("Done.")


if __name__ == "__main__":
    main()
