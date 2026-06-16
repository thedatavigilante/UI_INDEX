# UI_INDEX Environment Architecture & Structural Recommendation

## Executive Summary

**Current state:** Flat repo with mixed concerns. No publishing environment. No data generation automation. CI only validates — it doesn't produce or publish.

**Best practice recommendation:** Adopt a **3-environment Investigative Portfolio Architecture** (Dev → CI → Pages) with structural reorganization into `research/` and `portfolio/` directories.

---

## 1. Environment Analysis

### Current Environment Matrix (Detected)

| Concern | Dev (Local) | CI (GitHub) | Publish (None) | Portfolio (.io) |
|---------|-------------|-------------|----------------|-----------------|
| Python scripts | ✅ run | ✅ validate | ❌ | ❌ not linked |
| Notebooks | ✅ interactive | ❌ not run | ❌ | ❌ |
| JSON data | ✅ read/write | ✅ validate | ❌ | ❌ |
| PNG figures | ✅ view | ✅ count | ❌ | ❌ |
| API keys | ⚠️ env var | ❌ missing | N/A | N/A |
| Data generation | ✅ manual | ❌ automated | ❌ | ❌ |

**Critical gaps:**
1. **No publishing environment** — figures and notebooks are not viewable online
2. **No data generation automation** — CI validates but doesn't regenerate from APIs
3. **No portfolio bridge** — the .io site has no connection to this repo
4. **No environment separation** — dev/prod keys mixed in `.env.example`

---

## 2. Structural Assessment

### Current Structure (Flat)

```
ui_index/
├── api_client.py                    ← source code (root)
├── delta_analyzer.py                ← source code (root)
├── employer_contribution_gap.py     ← source code (root)
├── fec_integration_v251d.py         ← source code (root)
├── ... 12 Python files at root
├── ui_index_analysis.ipynb          ← notebook (root)
├── political_layer_analysis.ipynb  ← notebook (root)
├── data/                            ← data (nested)
│   ├── dmv_macro_baselines.csv
│   └── political/
│       ├── fec_funding_profiles.json
│       └── ... 6 JSON files
├── figures/                         ← outputs (nested)
│   └── *.png (10 files)
├── .github/workflows/               ← CI (nested)
│   └── validate.yml
├── README.md                        ← docs (root)
├── Slicers_and_Drilldown_Strategy.md ← docs (root)
└── requirements.txt                 ← config (root)
```

**Problems with flat structure:**
- **Mixed concerns:** 12 Python scripts at root = cognitive overload for newcomers
- **No separation of research vs. published artifacts:** Notebooks are source code AND deliverables
- **Data at risk of being treated as source:** JSON files in `data/` look like inputs but are outputs
- **No portfolio path:** Figures exist but aren't served anywhere

---

## 3. Recommended Architecture: Investigative Portfolio Pattern

### Directory Structure (Proposed)

```
ui_index/
├── .github/
│   └── workflows/
│       ├── validate.yml             ← CI: validate data integrity
│       ├── regenerate.yml           ← CI: scheduled data refresh (secrets needed)
│       └── publish.yml              ← CI: build GitHub Pages on data update
├── src/                             ← SOURCE CODE (treat as library)
│   ├── __init__.py
│   ├── api_client.py
│   ├── fec_integration.py           ← v251d (cycle-filtered)
│   ├── fec_integration_raw.py      ← raw investigative (multi-cycle)
│   ├── delta_analyzer.py
│   ├── political_layer_builder.py
│   ├── employer_contribution_gap.py
│   └── generate_charts.py          ← unified chart generator (all scenarios)
├── config/                          ← ENVIRONMENT CONFIGURATION
│   ├── dev.env                      ← dev API keys (gitignored, local only)
│   ├── prod.env.example             ← production key names (no values)
│   └── scenarios.yml                ← scenario parameters (Method A, C, D, E)
├── data/                            ← DATA (gitignored outputs, committed inputs only)
│   ├── raw/                         ← cached API responses (gitignored)
│   ├── processed/                   ← generated JSON (gitignored)
│   └── input/                       ← committed inputs (CSV, manual data)
│       └── dmv_macro_baselines.csv
├── research/                        ← RESEARCH NOTEBOOKS (development)
│   ├── ui_index_analysis.ipynb      ← BAI/WBI/MIPI analysis
│   ├── political_layer_analysis.ipynb
│   └── employer_contribution_gap.ipynb
├── portfolio/                       ← PUBLISHED ARTIFACTS (served by GitHub Pages)
│   ├── index.html                   ← landing page
│   ├── charts/                      ← static PNGs (copied from figures/)
│   ├── notebooks/                   ← notebook HTML exports (nbviewer-compatible)
│   └── data/                        ← public JSON (subset, no corruption_flags)
├── docs/                            ← DOCUMENTATION
│   ├── README.md                    ← main project overview
│   ├── methodology.md               ← math derivation, scenario comparison
│   ├── data_catalog.md              ← file inventory with lineage
│   ├── slicers_and_drilldown.md     ← interactive dashboard spec
│   └── glossary.md                  ← BAI, WBI, MIPI, SUI definitions
├── tests/                           ← VALIDATION TESTS
│   ├── test_data_integrity.py
│   ├── test_scenario_calculations.py
│   └── test_json_schema.py
├── requirements.txt                 ← Python dependencies
├── requirements-dev.txt             ← dev dependencies (pytest, black, etc.)
├── Makefile                         ← automation commands
└── .gitignore                       ← comprehensive ignore rules
```

### Environment Separation

| Environment | Directory | Purpose | API Keys | Data Freshness | Audience |
|-------------|-----------|---------|----------|----------------|----------|
| **Dev** | `research/` + `src/` | Notebook analysis, script development | `.env` local | Manual refresh | Sierra + collaborators |
| **CI** | `tests/` + `src/` | Validation, automated testing | `DEMO_KEY` only | Cached data | Code quality gate |
| **Data Gen** | `src/` + `data/raw/` | Scheduled API refresh | GitHub Secrets (production keys) | Auto-refresh daily/weekly | Pipeline |
| **Publish** | `portfolio/` | GitHub Pages static site | None | Snapshot of latest | Public readers |
| **Portfolio** | `gosidehustlesisi.github.io/` | External portfolio embed | None | Linked to `portfolio/` | Hiring managers, press |

---

## 4. The Three-Environment Decision

### Decision Matrix

| Option | Structure | Environments | Publishing | Effort | Best For |
|--------|-----------|--------------|------------|--------|----------|
| **A. Minimal** | Flat + `notebooks/` dir | Dev + CI | None | 1 hour | Quick fix only |
| **B. Cookiecutter** | Full `src/data/notebooks/docs/tests/` | Dev + CI + Docker | GitHub Pages | 4-6 hours | Large team, long-term |
| **C. Investigative Portfolio** (Recommended) | `src/`, `research/`, `portfolio/`, `docs/` | Dev + CI + Data-Gen + Pages | GitHub Pages + .io embed | 3-4 hours | **Portfolio + forensics hybrid** |

### Recommended: Option C (Investigative Portfolio)

**Why this wins:**

1. **Separates research from publication** — `research/` is messy, iterative, contains corruption_flags and raw investigative data. `portfolio/` is clean, public-facing, curated.

2. **Enables portfolio embed** — `portfolio/` becomes a GitHub Pages site. The .io portfolio can iframe or link to it. Figures are viewable without running Python.

3. **Environment isolation** — `config/dev.env` (local keys) and GitHub Secrets (production keys) are separate. No accidental commit of real keys.

4. **Scenario-based configuration** — `config/scenarios.yml` defines Method A, C, D, E parameters. The code reads from config, not hardcoded. Changing the scenario = changing one file.

5. **Automated data pipeline** — `regenerate.yml` runs on schedule, pulls fresh FEC data, regenerates JSON, runs validation, commits to `data/processed/`.

6. **Testable** — `tests/` validate: JSON schema, scenario math, figure generation, data integrity. CI runs these on every push.

---

## 5. Implementation Roadmap (If Approved)

### Phase 1: Structural Reorganization (1 hour)
1. Create `src/`, `research/`, `portfolio/`, `docs/`, `tests/`, `config/` directories
2. Move Python scripts → `src/`
3. Move notebooks → `research/`
4. Move markdown docs → `docs/`
5. Move `.env.example` → `config/dev.env.example`
6. Create `config/scenarios.yml` with Method A, C, D, E parameters
7. Update `.gitignore` for new structure

### Phase 2: Code Refactoring (1-2 hours)
1. Add `src/__init__.py` to make it a package
2. Update all imports (relative → `from src.api_client import ...`)
3. Refactor `employer_contribution_gap.py` to read from `config/scenarios.yml`
4. Create unified `generate_charts.py` that handles all scenarios
5. Add `tests/test_scenario_calculations.py` to verify each method's math

### Phase 3: Publishing Pipeline (1 hour)
1. Create `portfolio/index.html` with embedded charts
2. Add `publish.yml` GitHub Actions workflow:
   - On push to `main` with `data/` changes
   - Copy `figures/` → `portfolio/charts/`
   - Export notebooks to HTML → `portfolio/notebooks/`
   - Commit to `gh-pages` branch
3. Enable GitHub Pages from `gh-pages` branch

### Phase 4: Data Automation (1 hour)
1. Add `regenerate.yml` scheduled workflow (weekly)
2. Uses GitHub Secrets for FEC/Census API keys
3. Runs `fec_integration_v251d.py` and `political_layer_builder.py`
4. Validates outputs with `tests/test_data_integrity.py`
5. Commits updated data to `main` if validation passes

### Phase 5: Portfolio Bridge (30 min)
1. Update `gosidehustlesisi.github.io` to embed `ui_index` charts
2. Add `portfolio/data/` subset (public-safe JSON without raw investigation data)
3. Cross-link between .io portfolio and the GitHub Pages site

---

## 6. Cost-Benefit Analysis

| Concern | Current | Option C | Delta |
|---------|---------|----------|-------|
| Time to publish a figure | Manual screenshot | Auto-deployed on push | -90% |
| Time to add a new state | Edit 3+ files | Edit `config/scenarios.yml` + `data/input/` | -50% |
| Risk of exposing API keys | High (was in code) | Low (GitHub Secrets) | -95% |
| Portfolio presentation | No online view | GitHub Pages + .io embed | New capability |
| Data freshness | Stale (manual) | Weekly auto-refresh | New capability |
| Reproducibility | Manual steps | `make regenerate` + CI | +100% |
| Cognitive load | 12 files at root | 5 directories, clear roles | -60% |

---

## 7. Decision

**Recommend Option C: Investigative Portfolio Architecture.**

This is the best fit for the project's dual nature:
- **As forensics:** `research/` + `src/` + `config/scenarios.yml` supports rigorous, multi-methodology investigation
- **As portfolio:** `portfolio/` + GitHub Pages makes the work viewable without running Python
- **As automation:** `regenerate.yml` keeps data fresh without manual intervention

**Approval required for:**
1. The structural reorganization (Phase 1)
2. The GitHub Pages publishing setup (Phase 3)
3. The automated data regeneration (Phase 4, requires GitHub Secrets for API keys)

**Ready to execute all 5 phases upon approval.**
