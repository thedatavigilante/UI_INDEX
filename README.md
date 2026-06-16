<!-- markdownlint-disable -->

# ⚖️ The Stagnant Safety Net

<p align="center">
  <img src="https://github.com/thedatavigilante.png" width="120" alt="The Data Vigilante Logo">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/build-passing-success?style=flat-square" alt="Build Status">
  <img src="https://img.shields.io/badge/Data%20Validation-Verified-blue?style=flat-square" alt="Data Validation">
  <img src="https://img.shields.io/badge/Version-1.1.0-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-orange?style=flat-square" alt="License">
</p>

> ***A forensic data portfolio exposing how inflation, frozen policies, and political campaign contributions have been systematically weaponized to weaken unemployment insurance across the DMV.***

**Architected by:** Sierra Napier, MPA ([The Data Vigilante](https://github.com/thedatavigilante))  
**Target Focus:** District of Columbia, Maryland, Virginia (DMV) Legislative Auditing


---

## 🗺️ What This Is

This repository contains the data, code, and analysis behind an investigation into how unemployment insurance safety net adequacy has eroded across three jurisdictions — and who funds the legislators holding the policy levers.

It includes:
- **5 macroeconomic indices** (BAI, WBI, MIPI, Housing Gap, RVI) calculated from BLS, HUD, and Census data
- **8 economic/forensic charts** (matplotlib, figures 01–08, including the inflation-adjusted RVI) exported as PNGs
- **3 political funding charts** (FEC data, 2024 cycle) exported as PNGs — **11 figures total**
- **2 interactive Jupyter notebooks** for exploration and scenario analysis
- **A four-page portfolio site** (`index.html` + political/methodology/about) that embeds all 11 figures

---

## 📐 Forensic Metrics Defined

> *Notation: subscript `t` denotes a discrete comparative-static anchor year (2010, 2018, 2026) — see the Methodology Note below — not a continuous series.*

### 1. Benefit Adequacy Index (BAI)

$$
BAI_t = \frac{\text{Max WBA}_t}{\text{Weekly Housing Cost}_t}
$$

Isolates whether the maximum weekly benefit cap forces a choice between rent and immediate survival. **Any BAI < 1.0 indicates systemic failure** — the benefit does not cover housing alone.

### 2. Regressive Wage Base Index (WBI)

$$
WBI_t = \frac{\text{Taxable Wage Base}_t}{\text{Avg Annual Wage}_t}
$$

Tracks how much of the average worker's wage is actually subject to unemployment insurance taxation. As wages rise and the wage base stays frozen, the WBI falls — meaning employers pay into a shrinking share of the wage pool, narrowing the trust fund.

### 3. Multi-Income Penalty Index (MIPI)

$$
MIPI = \frac{\text{Side-Hustle Earnings} - \text{Disregard Threshold}}{\text{Max WBA}}
$$

Quantifies the institutional penalty on workers who earn supplementary income while receiving benefits. High MIPI = aggressive clawback that punishes resourcefulness and traps workers in dependency.

### 4. Housing Gap

$$
\text{Housing Gap}_t = \text{Weekly Housing Cost}_t - \text{Max WBA}_t
$$

The raw weekly survival deficit: how many dollars short a claimant is after benefits, before any other expenses.

### 5. Real Value Index (RVI) — inflation-adjusted

$$
RVI = \frac{\text{Max WBA}}{\left(\text{CPI}_{2026} / \text{CPI}_{\text{base}}\right)}
$$

Adjusts each frozen benefit by inflation (BLS CPI-U) to show its **real purchasing power today**. A frozen number isn't static — inflation cuts it every year, without a vote.

| State | Frozen at | Since | Real value 2026 | Erosion |
|-------|-----------|-------|-----------------|---------|
| Maryland | $430 | 2014 | **~$306** | −29% |
| Virginia | $378 | **2008** | **~$244** | −35% (worst) |
| DC | $444 | 2018 | **~$335** | −25% |

*Method: BLS CPI-U annual averages; 2014→2026 anchor = 40.67% ([in2013dollars/BLS](https://www.in2013dollars.com/us/inflation/2014?amount=430)). Chart: `figures/08_real_value_index.png`. Confirm exact figures against the BLS calculator before citing to the dollar. (Added 2026-06-12 — additive.)*

---

## 🔬 Methodology Note

This analysis uses **comparative static baselines** (2010, 2018, 2026) rather than continuous time-series or live API polling. The choice is intentional: benefit caps, wage bases, and disregard thresholds change through discrete legislative acts, not gradual drift. Anchoring to the same three moments across all three jurisdictions makes the policy decay visible and comparable — a moving average would obscure the step-function nature of the neglect.

Where live API data is used (FEC, Census ACS), the pipeline includes a self-healing client with caching and audit logging so rate limits don't corrupt the baseline record.

> **Current vs. planned:** the static-baseline approach above is what ships today and what every published figure reflects. A *rolling annual baseline* for the cost denominators (FMR, AWW) — designed to strip residual inflation-lag bias while preserving the step-function treatment of statutory ceilings — is **scoped but not yet implemented**. See the Roadmap below before citing any "rolling" or "dynamic" capability.

---

## 🛣️ Roadmap — Next Phase (scoped, in progress)

This is a **continuous work in progress**. The items below are designed and scoped but **not yet live** — they are listed here so the methodology stays honest about the line between what ships today and what's coming. The authoritative, itemized burndown is [`OPTIMIZATIONS.md`](OPTIMIZATIONS.md) (items #23–33); this is the human-readable summary.

**Status key:** ✅ done · 🔄 in progress · 📋 planned/scoped

### Phase 8 — Continuous baselines & live rates (📋 planned)
- 📋 **Rolling Annual Baseline Model** — evaluate cost denominators (HUD FMR, BLS AWW) on a rolling year-over-year window to remove inflation-lag bias. Statutory ceilings (Max WBA, wage base) stay step-function; only the cost vectors go continuous. *Current engine uses static 2010/2018/2026 baselines — this is the planned enhancement, not the shipped state.*
- 📋 **Dynamic SUI Tax Rate Matrix** — add a `fetch_dol_sui_rates.py` to pull live state experience-rating schedules from DOL, replacing the current static effective-rate assumption in `src/employer_models.py`. *(Script does not exist yet.)*

### Phase 6 — FEC methodology corrections (🔄 in progress; honest interim matrix already shipped)
- 📋 **Conduit / `memo_code` filter** (#24) — drop FEC pass-through (ActBlue/WinRed bundled) contributions that currently inflate business totals. *Not yet filtered — see `political.html` disclosure.*
- 📋 **Self-funding via transaction types** (#23) — use FEC loan codes (`15C/16C/15E/16E`) instead of name matching, which over-excludes Kaine/Warner/Hoyer joint-committee transfers.
- 📋 **B:L via `committee_type`** (#25) · **vendor exclusion** (#26) · **cycle normalization** (#27).
- ✅ **Four-section comparison matrix** — Raw / Self-Fund-Corrected / Verified B:L / Per-Month Normalized, shipped in `political.html` as the honest interim view pending the script fixes above.

### Phase 7 — Data governance (🔄 in progress)
- ✅ **Package migration** — scripts moved into the `src/` package (the old `fec_integration_v251d.py` is now `src/fec_pipelines.py`), tests added under `tests/`, deps pinned.
- 📋 Still open: `employer_contribution_gap.json` metadata-wrapper standardization, figure-numbering convention, data-placement cleanup (#30–33).

> When a roadmap item ships, it moves to ✅ here **and** the README prose that depends on it is updated in the same commit — code first, claim second. Nothing on this list should be described in the present tense elsewhere until it's checked off.

---

## 🗂️ Files in This Repository

### Package layout (`src/`)

The pipeline is a Python package; every module runs from the repo root as `python -m src.<module>` and resolves paths via the root-anchored constants in `src/__init__.py` (`ROOT`, `DATA`, `POLITICAL`, `FIGURES`).

```
src/
├── __init__.py                          # repo-root-anchored path constants
├── core_engine.py                       # BAI/WBI/MIPI/Housing Gap indices from the CSV baselines
├── employer_models.py                   # per-state employer contribution gap (frozen SUI base vs. expected)
├── fec_pipelines.py                     # FEC API (2024 cycle-filtered) → fec_funding_profiles.json
├── fec_integration_raw_investigative.py # multi-cycle raw pull for anomaly detection
├── fec_quick_test.py                    # FEC API connectivity diagnostic (NOT a data source)
├── political_layer_builder.py           # Congress.gov + Census ACS member enrichment
├── political_layer_analyzer.py          # pattern analysis over political_layer_report.json
├── delta_analyzer.py                    # cycle-filtered vs. multi-cycle corruption delta flags
├── api_client.py                        # self-healing API client (cache, retry, audit log)
└── charts/
    ├── generate_figures.py              # base index charts 01–04
    ├── generate_employer_gap_charts.py  # employer gap charts 05–07
    ├── generate_rvi_figure.py           # Real Value Index chart 08
    └── generate_fec_charts.py           # FEC funding charts 11–13

tests/        # pytest suite — test_core_math · test_political · test_data_integrity (locks the published numbers)
notebooks/    # 01_ui_index_analysis.ipynb · 02_political_layer_analysis.ipynb
docs/         # design specs — ENVIRONMENT_ARCHITECTURE.md · Slicers_and_Drilldown_Strategy.md
```

### Data Files (6 JSON + 1 CSV)

| File | Generated By | Content |
|------|-------------|---------|
| `data/dmv_macro_baselines.csv` | Manual / BLS | Base input data: wages, housing, benefit caps by jurisdiction and year |
| `data/political/fec_funding_profiles.json` | `src/fec_pipelines.py` | Cycle-filtered (2024) funding profiles with corruption flags |
| `data/political/fec_excluded_self_funding.json` | `src/fec_pipelines.py` | Excluded contributions (self-funding, multi-cycle, transfers) |
| `data/political/fec_quick_results.json` | `src/fec_quick_test.py` | Diagnostic test — **multi-cycle, NOT a data source** |
| `data/political/employer_contribution_gap.json` | `src/employer_models.py` | Per-state gap: frozen base vs. expected wage-indexed base |
| `data/political/political_layer_report.json` | `src/political_layer_builder.py` | Congress.gov members enriched with Census median income + committees |
| `data/political/fec_audit_log.json` | `src/api_client.py` | All API calls with status, timestamps, and cache hits |

### Figures (11 PNGs)

| File | Description |
|------|-------------|
| `figures/01_bai_decay_trajectory.png` | BAI decay 2010–2026 — all three jurisdictions crossing below 1.0 |
| `figures/02_wbi_stagnation.png` | WBI stagnation — wage base as share of average wage, frozen while wages rise |
| `figures/03_mipi_clawback.png` | MIPI clawback severity — penalty rate on supplementary earnings |
| `figures/04_housing_vs_wba_gap.png` | Housing cost vs. benefit gap — weekly survival deficit by state |
| `figures/05_employer_per_employee_gap.png` | Per-employee underpayment ($84–$157/worker/year) |
| `figures/06_employer_aggregate_gap.png` | Annual trust fund shortfall ($601.3M/year across DMV) |
| `figures/07_statutory_vs_expected_wage_base.png` | Statutory vs. expected wage base — what employers would pay if the base tracked wages |
| `figures/08_real_value_index.png` | **Real Value Index — frozen benefits vs. their inflation-adjusted 2026 value (MD ~$306, VA ~$244, DC ~$335)** |
| `figures/11_fec_total_receipts.png` | FEC total receipts by member |
| `figures/12_fec_business_vs_labor.png` | Business vs. labor contributions — committee chairs skew heavily business |
| `figures/13_fec_contribution_mix.png` | Contribution mix by category |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | This file |
| `DATA_CATALOG.md` | Full file inventory with lineage map and metadata standard |
| `OPTIMIZATIONS.md` | Running correction/burndown log (the authoritative roadmap) |
| `docs/ENVIRONMENT_ARCHITECTURE.md` | Future architecture proposal (not yet implemented) |
| `docs/Slicers_and_Drilldown_Strategy.md` | Interactive dashboard design specification (not yet implemented) |
| `index.html` | Portfolio landing page — embeds all 11 figures with methodology notes |
| `.env.example` | API key template (copy to `.env` and fill in your keys) |
| `requirements.txt` | Pinned Python dependencies |

### CI/CD

| File | Purpose |
|------|---------|
| `.github/workflows/validate.yml` | GitHub Actions — validates JSON, CSV, figures, and script syntax on every push |

---

## 🔑 Key Findings

| Jurisdiction | BAI 2010 | BAI 2026 | Δ BAI | Direction |
|-------------|----------|----------|-------|-----------|
| Maryland | 1.46 | 0.96 | **−0.50** | 🔴 BELOW THRESHOLD |
| Virginia | 1.40 | **1.02** | **−0.38** | 🟡 BARELY ABOVE (SB 1056, Jan 2026) |
| DC | 0.94 | 0.85 | **−0.09** | 🔴 BELOW THRESHOLD |

Maryland and DC operate below the survival threshold with no scheduled correction. Virginia passed **SB 1056** (effective January 4, 2026), raising the max WBA from $378 to **$430** — the first increase since 2014 — bringing its BAI to 1.02. Virginia is $10/week from failure. DC was already below threshold in 2010 and continues to deteriorate.

> **Data verified against live sources, 2026-06-11.** Virginia max WBA: [VEC official announcement](https://vec.virginia.gov/new-weekly-benefit-amounts-effective-january-4-2026). SUI wage bases: [EY Tax News](https://taxnews.ey.com/news/2026-0124-2026-state-unemployment-insurance-taxable-wage-bases). DC max WBA: [DC.gov Unemployment](https://unemployment.dc.gov/page/information-claimants). FEC totals: [FEC.gov](https://www.fec.gov/data/).

### Employer Contribution Gap
- **Per-employee underpayment:** $84–$157 per worker, per year
- **Aggregate trust fund shortfall:** **$601.3M/year** across DMV (using DOL historical effective SUI rates; a live experience-rating fetch is scoped in the [Roadmap](#️-roadmap--next-phase-scoped-in-progress) Phase 8)
  - Virginia: $252.4M/year
  - Maryland: $248.6M/year
  - DC: $100.3M/year
- **Wage base erosion:** MD base is now 11.7% of average wage (down from 16.3% in 2010); VA 11.7% (down from 16.7%); DC 8.0% (down from 13.6%)

### Political Accountability: Who Funds the Freeze
- **7 members** with UI-relevant committee assignments analyzed using FEC 2023-2024 reporting period data
- **$89.9M** in total committee activity; once David Trone's $62.9M in *verified candidate self-loans* are correctly removed (98.7% of his $63.83M cycle receipts), **$27.0M** is true outside money
- **David Trone** co-founded Total Wine & More (~$2.4B company) and sat on the **Ways and Means Committee** while self-funding 98.7% of his Senate campaign
- **No labor-affiliated PAC contribution above $500** reached Hoyer, Kaine, or Warner in the cycle
- **Cline (13:1)** and **Ruppersberger (21:1)** are the only members with enough business/labor categorization coverage (7% and 30%) for a directionally meaningful ratio; others are honestly marked *insufficient coverage*
- **Methodology honesty:** raw FEC categorization is misleading in three ways (self-funding contamination, weak business/labor coverage, no cycle normalization). The [Political Layer page](https://thedatavigilante.github.io/UI_INDEX/political.html) shows a **four-view comparison matrix** with every caveat labeled — see also the correction roadmap in [`OPTIMIZATIONS.md`](OPTIMIZATIONS.md) items 23–29.
- **Note:** Mark Warner (VA, 2026 race) and Chris Van Hollen (MD, ~2028 race) were not 2024 candidates; their figures represent off-cycle committee fundraising

### Lawmaker Salary vs. UI Benefit: The Contrast

| Body | Their pay change (2014–2026) | UI max WBA change (2014–2026) |
|------|------------------------------|-------------------------------|
| MD General Assembly | +$6,306 (+12.5%) via auto Compensation Commission | **+$0 (0%)** — frozen 12 years |
| VA General Assembly | +$32,360 (+183%) proposed 2026 | +$52 (+13.8%) — first change since 2014 |
| DC Council | +CPI auto-linked (~+15%) | +$85 (+23.7%) — still below survival threshold |
| U.S. Congress | $0 (0%) — $174K frozen since 2009 | N/A (federal FUTA floor only) |

Sources: [MD Compensation Commission 2026](https://mgaleg.maryland.gov/Pubs/Other/2026-Report-of-the-General-Assembly-Compensation-Commission.pdf) · [CRS RL30064 Congressional Salaries](https://www.congress.gov/crs-product/RL30064) · [WSET — VA legislator pay raise](https://wset.com/news/local/virginia-senate-democrats-pass-state-budget-add-nearly-300-percent-pay-increase-for-legislators-money-taxes-richmond-republicans-amendments-affordability) (headline says "nearly 300%" off a different baseline; the $17,640→$50,000 figure = **+183%**) · [DC Code §1-611.09](https://code.dccouncil.gov/us/dc/council/code/sections/1-611.09)

---

## 🚀 Quickstart

### 1. Set up environment

```bash
# Create and activate the virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set up API keys

```bash
cp .env.example .env
# Edit .env with your real keys
```

- **FEC API key:** https://api.open.fec.gov/developers/
- **Census API key:** https://api.census.gov/data/key_signup.html

Congress.gov uses `DEMO_KEY` (public, no signup required for basic use).

All modules run as packages from the repo root (`python -m src.<module>`), so paths resolve regardless of working directory.

### 3. Generate the base analysis

```bash
python -m src.core_engine
python -m src.charts.generate_figures
```

### 4. Generate the employer contribution gap

```bash
python -m src.employer_models
python -m src.charts.generate_employer_gap_charts
```

### 5. Generate the political funding layer

```bash
python -m src.fec_pipelines
python -m src.charts.generate_fec_charts
python -m src.political_layer_builder
```

### 6. Run the delta analysis (corruption detection)

```bash
python -m src.delta_analyzer
```

### 7. Run the tests

```bash
python -m pytest tests/ -q
```

---

## 🔧 Data Provenance

Every JSON data file includes a `_metadata` block documenting:
- **Generated by:** Which script produced it
- **Generated at:** Timestamp
- **Cycle:** Election year (for FEC data) or analysis year
- **Data sources:** BLS, USDOL, FEC, Census, Congress.gov
- **Methodology:** How the numbers were calculated
- **Caveat:** Known limitations and approximations

See `DATA_CATALOG.md` for the full file inventory with lineage.

---

## 📊 Key Metrics

| Index | Formula | What It Measures |
|-------|---------|------------------|
| **BAI** | Max WBA ÷ Weekly Housing Cost | Can benefits cover rent? |
| **WBI** | Taxable Wage Base ÷ Avg Annual Wage | Is the tax base regressing? |
| **MIPI** | (Earnings − Disregard) ÷ Max WBA | Poverty trap for part-time workers |
| **Housing Gap** | Weekly Housing − Max WBA | Survival deficit per week |
| **RVI** | Max WBA ÷ (CPI₂₀₂₆ ÷ CPI_base) | Real purchasing power of a frozen benefit today |

---

## ⚠️ Known Limitations

- **Campaign finance categorization** uses keyword matching on contributor names (approximate). For production use, official FEC committee IDs should be used.
- **Business/labor categorization** is based on string patterns, not official industry codes.
- **Self-funding detection** uses last-name matching and may include false positives.
- **Avg wages and covered employment** in the employer gap are approximate BLS estimates.
- **The employer gap methodology** uses the 2010-ratio approach (Method B). Alternative methodologies (full wage base, CPI-only, national peer average, wage growth index) would produce different dollar figures. See the source code for scenario definitions.
- **Several of these are scoped fixes, not permanent gaps** — the transaction-type self-funding detection, conduit/`memo_code` filter, and `committee_type` categorization are tracked in the [Roadmap](#️-roadmap--next-phase-scoped-in-progress) and [`OPTIMIZATIONS.md`](OPTIMIZATIONS.md) #23–33. Disclosed openly rather than hidden.

---

## 📁 Portfolio — Four-Page Static Site

The portfolio is a four-page GitHub Pages site (pure HTML/CSS/JS, no build step):

| Page | Purpose |
|------|---------|
| [`index.html`](https://thedatavigilante.github.io/UI_INDEX/) | The audit — 5 chapters, charts, investigative takes, cross-index severity banner, lawmaker salary contrast |
| [`political.html`](https://thedatavigilante.github.io/UI_INDEX/political.html) | Political layer — four-view FEC comparison matrix, Trone profile, lawmaker deep-dive, methodology disclosure |
| [`methodology.html`](https://thedatavigilante.github.io/UI_INDEX/methodology.html) | Data transparency — live-source validation table, formulas, housing cost methodology, limitations |
| [`about.html`](https://thedatavigilante.github.io/UI_INDEX/about.html) | The Data Vigilante — bio, what was built, fractional CDO offer, hire me |

The running correction log is in [`OPTIMIZATIONS.md`](OPTIMIZATIONS.md). For interactive notebooks:

- [BAI/WBI/MIPI Analysis](https://nbviewer.org/github/thedatavigilante/UI_INDEX/blob/main/notebooks/01_ui_index_analysis.ipynb)
- [Political Layer Analysis](https://nbviewer.org/github/thedatavigilante/UI_INDEX/blob/main/notebooks/02_political_layer_analysis.ipynb)

---

## 🔗 Repository

https://github.com/thedatavigilante/UI_INDEX

---

*Built for policymakers, journalists, and anyone who believes a safety net should actually catch people.*
