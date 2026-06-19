# Contributing to UI_INDEX

The Stagnant Safety Net is a forensic data portfolio. The published figures are
receipts — changes that alter a public number must be justified and locked by a test.

## Repository layout (src layout)

```
src/ui_index/      Importable analytics package (engine, models, FEC pipelines, API client)
tools/             Operational scripts — data fetchers (fetch_*) and figure generators (generate_*)
tests/             pytest suite (data integrity + index/political regression locks)
data/              Source CSV + cached JSON (three-tier fallback pattern)
figures/  interactive/  maps/  notebooks/  dashboard/   Generated/static artifacts
index.html  political.html  about.html  methodology.html   GitHub Pages site
```

Why src layout: it prevents accidentally importing the in-tree package instead of
the installed one, so tests exercise what users actually install
([PyPA guidance](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout)).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .                  # installs the ui_index package (editable)
pip install -r requirements-dev.txt
```

## Run order (full refresh)

All scripts are run **from the repository root**:

```bash
# Fetch (needs API keys in .env or GitHub Secrets)
python tools/fetch_fred_inflation.py
python tools/fetch_bls_baselines.py
python tools/fetch_housing.py
python tools/fetch_dol_sui_rates.py
python tools/fetch_usaspending.py
python tools/fetch_county_data.py

# Generate figures / maps / interactive
python tools/generate_figures.py
python tools/generate_rvi_figure.py
python tools/generate_employer_gap_charts.py
python tools/generate_fec_charts.py
python tools/generate_context_figure.py
python tools/generate_spending_accountability.py
python tools/generate_county_map.py
python tools/generate_plotly_charts.py
```

The analytics package is importable directly:

```python
from ui_index.core_engine import UIIndexEngine
print(UIIndexEngine().compute_indices())
```

## Tests

```bash
pytest tests/ -v
```

- `test_data_integrity.py` — schema/data-file integrity
- `test_core_math.py` — locks BAI/WBI/MIPI/RVI published values
- `test_political.py` — locks reconciled FEC figures ($27.0M true-outside-money)

If a CSV update legitimately changes a published number, update the corresponding
assertion **and** the figure/HTML in the same PR. Never loosen a lock to make CI pass.

## Three-tier fallback (do not break)

Every data-dependent script follows: **live API → cached JSON → hardcoded verified value.**
This keeps the repo runnable without keys and regenerable when an API is down.
