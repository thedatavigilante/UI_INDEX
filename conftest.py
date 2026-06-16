"""Root conftest — ensures the repo root is importable so `from src import ...` works
under pytest regardless of invocation directory."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
