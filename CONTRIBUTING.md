# Contributing to UI_INDEX

Thank you for contributing to The Stagnant Safety Net forensic data portfolio.

## Package Structure

All Python source lives under `src/` — a proper package with path-constant exports:

```
src/
  __init__.py            # ROOT, DATA, POLITICAL, FIGURES path constants
    core_engine.py         # BAI/WBI/MIPI/Housing Gap indices
      employer_models.py     # SUI contribution gap calculator
        fec_pipelines.py       # FEC API integration (2024 cycle)
          delta_analyzer.py      # Corruption detection (cycle vs multi-cycle delta)
            api_client.py          # Self-healing API client (cache, retry, audit log)
              political_layer_builder.py
                political_layer_analyzer.py
                  fec_integration_raw_investigative.py
                    fec_quick_test.py
                      charts/
                          generate_figures.py          # Base index charts 01-04
                              generate_employer_gap_charts.py
                                  generate_rvi_figure.py       # Real Value Index chart 08
                                      generate_fec_charts.py       # FEC funding charts 11-13

                                      tests/
                                        test_core_math.py      # Regression locks — published index values
                                          test_data_integrity.py # Data file provenance + figure existence
                                            test_political.py      # FEC reconciled figures
                                            conftest.py              # sys.path injection for pytest
                                            ```

                                            **All commands must be run from the repository root** (the directory containing `pyproject.toml`), so that `from src import ...` resolves correctly.

                                            ## Setup

                                            ```bash
                                            python -m venv .venv
                                            source .venv/bin/activate          # Windows: .venv\Scripts\activate
                                            pip install -r requirements.txt    # Core pipeline + pytest
                                            pip install -r requirements-dev.txt  # Optional: notebooks, plotly, streamlit
                                            cp .env.example .env               # Add your API keys
                                            ```

                                            ## Running Tests

                                            ```bash
                                            # All tests (from repo root)
                                            python -m pytest tests/ -q

                                            # Verbose with specific modules
                                            python -m pytest tests/test_core_math.py tests/test_data_integrity.py -v --tb=short
                                            ```

                                            Tests are regression locks — `test_core_math.py` pins the published BAI/WBI/MIPI/RVI values. If you update the CSV baselines, update the test assertions in the same commit.

                                            ## Regenerating Figures

                                            ```bash
                                            # Core index charts (01-04)
                                            python -m src.charts.generate_figures

                                            # Employer gap charts (05-07)
                                            python -m src.employer_models
                                            python -m src.charts.generate_employer_gap_charts

                                            # Real Value Index chart (08)
                                            python -m src.charts.generate_rvi_figure

                                            # FEC funding charts (11-13)
                                            python -m src.fec_pipelines          # requires FEC_API_KEY in .env
                                            python -m src.charts.generate_fec_charts

                                            # Political layer
                                            python -m src.political_layer_builder
                                            python -m src.delta_analyzer
                                            ```

                                            ## Commit Convention

                                            This repo uses conventional commits. Match the style in the commit history:

                                            | Prefix | When to use |
                                            |--------|-------------|
                                            | `feat:` | New analysis capability or portfolio page |
                                            | `fix:` | Bug fix in computation or CI |
                                            | `test:` | Adding or updating tests |
                                            | `chore:` | Dependency, tooling, config changes |
                                            | `docs:` | README, DATA_CATALOG, methodology docs |
                                            | `refactor:` | Code restructure without behavior change |

                                            ## Data Files

                                            Committed JSON files in `data/political/` are the forensic receipts — do not gitignore them. Every JSON must include a `_metadata` provenance block (see `DATA_CATALOG.md`).

                                            ## CI

                                            The `validate.yml` workflow runs on every push and PR to `main`:
                                            1. Validate JSON data files
                                            2. Validate CSV baseline
                                            3. Check figure count (≥10 PNGs)
                                            4. FEC data quality check
                                            5. Syntax check (`find src -name "*.py" -exec python3 -m py_compile {} +`)
                                            6. Data integrity + math regression tests (`pytest tests/test_data_integrity.py tests/test_core_math.py -v --tb=short`)
                                            7. Full test suite (`pytest tests/ -q --tb=short`)
                                            8. Verify no `__pycache__` committed

                                            The data-refresh workflow (`data_refresh.yml`) requires `FEC_API_KEY` and `REQUIRE_API_KEY` set as GitHub Actions secrets.
                                            
