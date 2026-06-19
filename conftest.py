"""Make the src-layout package importable under pytest without requiring an
editable install. `pip install -e .` is the canonical path (used in CI); this
fallback keeps `pytest` working from a bare checkout too.
"""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
