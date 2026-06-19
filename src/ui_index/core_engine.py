import csv
import os
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from tabulate import tabulate
except ImportError:
    tabulate = None


class UIIndexEngine:
    """
    The Data Vigilante // Comparative Static Forensic Auditor
    Reads documented baselines from CSV and computes safety net decay indices.
    """

    DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "dmv_macro_baselines.csv"

    def __init__(self, data_path=None):
        self.data_path = data_path or self.DATA_PATH
        self.baselines = self._load_baselines()

    def _load_baselines(self):
        """Load documented baseline data from CSV."""
        records = []
        if not self.data_path.exists():
            raise FileNotFoundError(f"Baseline data not found: {self.data_path}")

        with open(self.data_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append({
                    "jurisdiction": row["Jurisdiction"],
                    "year": int(row["Year"]),
                    "max_wba": float(row["Max_WBA"]),
                    "taxable_wage_base": float(row["Taxable_Wage_Base"]),
                    "avg_annual_wage": float(row["Avg_Annual_Wage"]),
                    "weekly_housing": float(row["Weekly_Housing"]),
                })
        return records

    def compute_indices(self, side_hustle_earnings=250, income_disregard=50):
        """
        Compute BAI, WBI, and MIPI for all baseline records.
        """
        results = []
        for rec in self.baselines:
            bai = rec["max_wba"] / rec["weekly_housing"]
            wbi = rec["taxable_wage_base"] / rec["avg_annual_wage"]
            net_counted = max(0, side_hustle_earnings - income_disregard)
            mipi = net_counted / rec["max_wba"] if rec["max_wba"] > 0 else 0

            results.append({
                "Jurisdiction": rec["jurisdiction"],
                "Year": rec["year"],
                "Max_WBA": rec["max_wba"],
                "Weekly_Housing": rec["weekly_housing"],
                "BAI": round(bai, 2),
                "WBI": round(wbi, 4),
                "MIPI": round(mipi, 2),
                "Systemic_Status": "CRITICAL DECAY" if bai < 1.0 else "STABLE",
            })
        return results

    def trend_summary(self):
        """Compute year-over-year deltas for each jurisdiction."""
        indices = self.compute_indices()
        df = pd.DataFrame(indices) if pd else None
        if df is None:
            return None

        summary = []
        for jurisdiction in df["Jurisdiction"].unique():
            sub = df[df["Jurisdiction"] == jurisdiction].sort_values("Year")
            if len(sub) >= 2:
                bai_delta = sub.iloc[-1]["BAI"] - sub.iloc[0]["BAI"]
                wbi_delta = sub.iloc[-1]["WBI"] - sub.iloc[0]["WBI"]
                summary.append({
                    "Jurisdiction": jurisdiction,
                    "BAI_Change_2010_2026": round(bai_delta, 2),
                    "WBI_Change_2010_2026": round(wbi_delta, 4),
                    "Direction": "WORSENING" if bai_delta < 0 else "IMPROVING",
                })
        return summary

    def generate_dashboard(self, side_hustle_earnings=250):
        """Execute full pipeline and return formatted dashboard."""
        indices = self.compute_indices(side_hustle_earnings)
        if pd:
            return pd.DataFrame(indices)
        return indices


def format_dashboard(records):
    if isinstance(records, list):
        headers = [
            "Jurisdiction", "Year", "Max_WBA", "Weekly_Housing",
            "BAI", "WBI", "MIPI", "Systemic_Status"
        ]
        rows = [headers] + [[str(record[h]) for h in headers] for record in records]
        widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
        lines = []
        for row in rows:
            lines.append(" | ".join(val.ljust(widths[i]) for i, val in enumerate(row)))
        return "\n".join(lines)

    if hasattr(records, "to_markdown"):
        return records.to_markdown(index=False)

    if tabulate and hasattr(records, "to_dict"):
        return tabulate(records.to_dict("records"), headers="keys", tablefmt="github")

    return str(records)


def print_trend_summary(engine):
    summary = engine.trend_summary()
    if summary:
        print("\n📈 Trend Summary (2010 → 2026):")
        if pd:
            print(pd.DataFrame(summary).to_markdown(index=False))
        else:
            for s in summary:
                print(f"  {s['Jurisdiction']}: BAI {s['BAI_Change_2010_2026']:+.2f} ({s['Direction']})")


if __name__ == "__main__":
    print("🔍 Loading documented baselines from data/dmv_macro_baselines.csv...\n")
    engine = UIIndexEngine()
    dashboard = engine.generate_dashboard(side_hustle_earnings=250)
    print(format_dashboard(dashboard))
    print_trend_summary(engine)
