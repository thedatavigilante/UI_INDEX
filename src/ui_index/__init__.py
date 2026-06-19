"""UI_INDEX forensic analytics package — The Stagnant Safety Net.

Single source of truth for repo-root-anchored paths so modules resolve data
regardless of the current working directory. Mirrors the three-tier fallback
pattern documented in CLAUDE.md.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repository root (src/ui_index/ -> repo)
DATA = ROOT / "data"
POLITICAL = DATA / "political"
FIGURES = ROOT / "figures"

__all__ = ["ROOT", "DATA", "POLITICAL", "FIGURES"]
