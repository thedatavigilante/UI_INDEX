#!/usr/bin/env python3
"""
Delta Analyzer — Investigative Corruption Detection
Compares cycle-filtered (v251d) vs raw multi-cycle (investigative) data.
The delta IS the corruption signal.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from src import DATA, POLITICAL, FIGURES  # repo-root-anchored paths


def load_profiles(path: Path) -> List[Dict]:
        with open(path) as f:
                    data = json.load(f)
                # Handle both wrapped (with _metadata) and unwrapped formats
                if isinstance(data, dict) and "data" in data:
                            return data["data"]
                        return data


def analyze_delta(cycle_path: Path, raw_path: Path) -> Dict:
        """Compare cycle-filtered vs raw data to detect corruption patterns."""

    cycle_profiles = {p["name"]: p for p in load_profiles(cycle_path)}
    raw_profiles = {p["name"]: p for p in load_profiles(raw_path)}

    deltas = []

    for name, raw in raw_profiles.items():
                cycle = cycle_profiles.get(name)
                if not cycle:
                                continue

                raw_total = raw.get("total_receipts", 0) or 0
                cycle_total = cycle.get("total_receipts", 0) or 0

        delta = raw_total - cycle_total
        delta_pct = (delta / cycle_total * 100) if cycle_total > 0 else 0

        flags = []

        # HIGH: Multi-cycle money exceeding current cycle total
        if delta > cycle_total:
                        flags.append({
                                            "severity": "HIGH",
                                            "type": "multi_cycle_exceeds_current",
                                            "description": f"Multi-cycle total (${raw_total:,.0f}) exceeds current cycle (${cycle_total:,.0f}) by {delta_pct:.0f}%",
                                            "indicator": "Candidate's financial activity spans multiple cycles at a scale dwarfing current election. May indicate: \
                            (1) Rolling committee structures that recycle funds indefinitely, \
                            (2) Self-funding loans carried across cycles, \
                            (3) Dark money routed through multi-cycle PACs"
                        })

        # MEDIUM: Significant multi-cycle bleed (>20%)
        elif delta_pct > 20:
                        flags.append({
                                            "severity": "MEDIUM",
                                            "type": "significant_multi_cycle",
                                            "description": f"{delta_pct:.0f}% of financial activity from other cycles (${delta:,.0f})",
                                            "indicator": "Substantial cross-cycle funding. May indicate strategic reallocation or committee restructuring to obscure donor origins."
                        })

        # Check for self-funding patterns across cycles
        raw_excluded = raw.get("excluded_itemized", 0) or raw.get("excluded_self_funding", 0)
        cycle_excluded = cycle.get("excluded_itemized", 0) or cycle.get("excluded_self_funding", 0)

        if raw_excluded > cycle_excluded * 2:
                        flags.append({
                                            "severity": "MEDIUM",
                                            "type": "escalating_self_funding",
                                            "description": f"Self-funding/other exclusions {raw_excluded/cycle_excluded:.1f}x higher in multi-cycle view",
                                            "indicator": "Candidate may be using multi-cycle structures to bypass individual contribution limits or conceal true funding sources."
                        })

        # Check for committee-to-committee transfer patterns
        raw_pac = raw.get("pac_contributions", 0) or 0
        cycle_pac = cycle.get("pac_contributions", 0) or 0

        if raw_pac > cycle_pac * 1.5:
                        flags.append({
                                            "severity": "MEDIUM",
                                            "type": "pac_transfer_inflation",
                                            "description": f"PAC contributions {raw_pac/cycle_pac:.1f}x higher in multi-cycle view (${raw_pac:,.0f} vs ${cycle_pac:,.0f})",
                                            "indicator": "PAC money may be routed through multiple committees across cycles to evade contribution limits or disclosure requirements."
                        })

        deltas.append({
                "name": name,
                "state": raw.get("state", ""),
                "cycle_total": cycle_total,
                "raw_total": raw_total,
                "delta": delta,
                "delta_pct": round(delta_pct, 1),
                "flags": flags,
                "investigative_priority": "HIGH" if any(f["severity"] == "HIGH" for f in flags) else \
                    "MEDIUM" if any(f["severity"] == "MEDIUM" for f in flags) else "LOW"
        })

    # Sort by investigative priority then delta magnitude
        deltas.sort(key=lambda x: (
                    0 if x["investigative_priority"] == "HIGH" else 1 if x["investigative_priority"] == "MEDIUM" else 2,
                    -abs(x["delta"])
        ))

    return {
                "_metadata": {
                                "generated_by": "delta_analyzer.py",
                                "generated_at": "2026-06-11T00:00:00Z",
                                "purpose": "Investigative corruption detection — delta between cycle-filtered and multi-cycle data",
                                "methodology": "Compares fec_funding_profiles.json (cycle=2024) against raw multi-cycle data. \
                    Discrepancies indicate cross-cycle financial engineering that may obscure true funding sources.",
                                "data_sources": [
                                                    "FEC API v1 (cycle-filtered: v251d)",
                                                    "FEC API v1 (multi-cycle: raw_investigative)"
                                ]
                },
                "summary": {
                                "total_analyzed": len(deltas),
                                "high_priority": sum(1 for d in deltas if d["investigative_priority"] == "HIGH"),
                                "medium_priority": sum(1 for d in deltas if d["investigative_priority"] == "MEDIUM"),
                                "low_priority": sum(1 for d in deltas if d["investigative_priority"] == "LOW"),
                },
                "deltas": deltas
    }
