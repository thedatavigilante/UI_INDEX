"""UI_INDEX forensic analytics package.

Single source of truth for repo-root-anchored paths so modules work no matter
the current working directory (run as `python -m src.core_engine` from root).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # repository root
DATA = ROOT / "data"
POLITICAL = DATA / "political"
FIGURES = ROOT / "figures"

__all__ = ["ROOT", "DATA", "POLITICAL", "FIGURES"]
