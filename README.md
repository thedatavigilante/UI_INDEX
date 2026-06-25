<!-- markdownlint-disable -->

# ⚖️ The Stagnant Safety Net

<p align="center">
  <img src="https://github.com/thedatavigilante.png" width="120" alt="The Data Vigilante Logo">
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/thedatavigilante/UI_INDEX?style=social" alt="GitHub stars">
  <img src="https://img.shields.io/github/forks/thedatavigilante/UI_INDEX?style=social" alt="GitHub forks">
  <img src="https://img.shields.io/github/last-commit/thedatavigilante/UI_INDEX" alt="Last commit">
  <img src="https://github.com/thedatavigilante/UI_INDEX/actions/workflows/validate.yml/badge.svg" alt="CI">
  <img src="https://img.shields.io/github/license/thedatavigilante/UI_INDEX" alt="License">
  <a href="https://thedatavigilante.github.io/UI_INDEX/"><img src="https://img.shields.io/badge/Live%20Site-thedatavigilante.github.io%2FUI__INDEX-FFB800?logo=githubpages" alt="Live Site"></a>
</p>

> ***A forensic data portfolio exposing how inflation, frozen policies, and political campaign contributions have been systematically weaponized to weaken unemployment insurance across the DMV.***

**Architected by:** Sierra Napier, MPA ([The Data Vigilante](https://github.com/thedatavigilante))  
**Target Focus:** District of Columbia, Maryland, Virginia (DMV) Legislative Auditing

---

## 🚀 6-Second Scan

| Stat | Value | What it means |
|------|-------|---------------|
| 🔴 **Maryland BAI 2026** | **0.96** | Benefits can't cover rent |
| 🔴 **DC BAI 2026** | **0.85** | $76/week short on housing |
| 🟡 **Virginia BAI 2026** | **1.02** | $10/week from failure (SB 1056) |
| 💰 **DMV Annual Shortfall** | **$601.3M** | Trust fund starved by frozen caps |
| 🏛️ **MD wage base** | **$8,500** | Frozen since **1992** |
| 📊 **Political analysis** | **7 members** | $89.9M in committee activity; B:L ratios up to 21:1 |

**[→ Live Portfolio](https://thedatavigilante.github.io/UI_INDEX/)** · **[→ Political Layer](https://thedatavigilante.github.io/UI_INDEX/political.html)** · **[→ Methodology](https://thedatavigilante.github.io/UI_INDEX/methodology.html)** · **[→ About](https://thedatavigilante.github.io/UI_INDEX/about.html)**

---

## 📑 Table of Contents

- [What This Is](#-what-this-is)
- [Forensic Metrics Defined](#-forensic-metrics-defined)
- [Methodology Note](#-methodology-note)
- [Files in This Repository](#-files-in-this-repository)
- [Key Findings](#-key-findings)
- [Quickstart](#-quickstart)
- [Data Provenance](#-data-provenance)
- [Known Limitations](#-known-limitations)
- [Portfolio](#-portfolio)

---

## 🗺️ What This Is

This repository contains the data, code, and analysis behind an investigation into how unemployment insurance safety net adequacy has eroded across three jurisdictions — and who funds the legislators holding the policy levers.

It includes:
- **4 macroeconomic indices** (BAI, WBI, MIPI, Housing Gap) calculated from BLS and Census data
- **7 static visualization charts** (matplotlib) exported as PNGs
- **3 political funding charts** (FEC data, 2024 cycle) exported as PNGs
- **2 interactive Jupyter notebooks** for exploration and scenario analysis
- **A portfolio landing page** (`index.html`) that embeds all figures

---

## 📐 Forensic Metrics Defined

### 1. Benefit Adequacy Index (BAI)
`BAI = Max_WBA ÷ Weekly_Housing_Cost`

Isolates whether the maximum weekly benefit cap forces a choice between rent and immediate survival. **Any BAI < 1.0 indicates systemic failure** — the benefit does not cover housing alone.

### 2. Regressive Wage Base Index (WBI)
`WBI = Taxable_Wage_Base ÷ Avg_Annual_Wage`

Tracks how much of the average worker's wage is actually subject to unemployment insurance taxation. As wages rise and the wage base stays frozen, the WBI falls — meaning employers pay into a shrinking share of the wage pool, narrowing the trust fund.

### 3. Multi-Income Penalty Index (MIPI)
`MIPI = (Side_Hustle_Earnings − Disregard_Threshold) ÷ Max_WBA`

Quantifies the institutional penalty on workers who earn supplementary income while receiving benefits. High MIPI = aggressive clawback that punishes resourcefulness and traps workers in dependency.

### 4. Housing Gap
`Housing_Gap = Weekly_Housing_Cost − Max_WBA`

The raw weekly survival deficit: how many dollars short a claimant is after benefits, before any other expenses.

### 5. Real Value Index (RVI) — inflation-adjusted
`RVI = Max_WBA ÷ (CPI₂₀₂₆ ÷ CPI_base_year)`

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

---

## 🗂️ Files in This Repository

### Python Scripts (22 files)

**Data fetch pipeline** (run in this order to refresh data):

| File | Purpose |
|------|---------|
| `fetch_fred_inflation.py` | FRED API — CPI-U + DC metro CPI + PCE; saves `data/inflation_crosscheck.json` |
| `fetch_bls_baselines.py` | BLS QCEW wages + CPI-U + LAUS unemployment rates; updates `dmv_macro_baselines.csv` |
| `fetch_housing.py` | HUD FMR API — 2BR Fair Market Rents → weekly housing proxies |
| `fetch_dol_sui_rates.py` | DOL ETA-5159 CSV — effective SUI tax rates; saves `data/sui_rates.json` |
| `fetch_usaspending.py` | USASpending.gov CFDA 17.225 — federal UI grants by state |
| `fetch_county_data.py` | BLS LAUS county unemployment + Census ACS county income |

**Visualization scripts**:

| File | Purpose |
|------|---------|
| `generate_figures.py` | Generates the 4 base charts (01–04) from CSV data |
| `generate_rvi_figure.py` | Real Value Index figure (08) — inflation-adjusted benefit values |
| `generate_employer_gap_charts.py` | Employer gap charts (05–07) |
| `generate_fec_charts.py` | FEC funding charts (11–13) |
| `generate_context_figure.py` | Figure 09 — unemployment context (BLS LAUS + USASpending) |
| `generate_spending_accountability.py` | Figure 10 — employer money vs. federal UI investment scatter |
| `generate_county_map.py` | Folium choropleth → `maps/dmv_counties.html` |
| `generate_plotly_charts.py` | 11 interactive Plotly HTML charts → `interactive/` |

**Analysis scripts**:

| File | Purpose |
|------|---------|
| `ui_index_engine.py` | Calculates BAI/WBI/MIPI/Housing Gap indices |
| `employer_contribution_gap.py` | Per-state employer contribution gap (frozen SUI vs. expected) |
| `fec_integration_v251d.py` | FEC API integration (2024 cycle-filtered, production) |
| `political_layer_builder.py` | Congress.gov + Census ACS enrichment |
| `political_layer_analyzer.py` | Analyzes political patterns from `political_layer_report.json` |
| `delta_analyzer.py` | Corruption delta flags comparing cycle-filtered vs. multi-cycle FEC |
| `api_client.py` | Self-healing API client with caching, retry, and audit logging |

**Dashboard**:

```bash
streamlit run dashboard/app.py
```
Runs a live Streamlit dashboard with 5 tabs: BAI/WBI/MIPI indices, employer gap, FEC funding,
county map, and data refresh controls. Requires API keys in environment.

### Notebooks (6 files)

**Root-level (legacy, linked via nbviewer):**

| File | Purpose |
|------|---------|
| `ui_index_analysis.ipynb` | BAI/WBI/MIPI/Housing Gap analysis — interactive exploration |
| `political_layer_analysis.ipynb` | Political funding + committee analysis — interactive exploration |

**`/notebooks/` directory (rebuilt elite stack):**

| File | Purpose |
|------|---------|
| `notebooks/01_data_pipeline.ipynb` | End-to-end data pipeline walkthrough — fetch, validate, cache |
| `notebooks/02_ui_index_analysis.ipynb` | Deep-dive on BAI/WBI/MIPI with Plotly charts |
| `notebooks/03_political_layer.ipynb` | FEC + Census + committee analysis |
| `notebooks/04_county_gis.ipynb` | County-level GIS: Folium map + choropleth generation |

### Data Files (6 JSON + 1 CSV)

| File | Generated By | Content |
|------|-------------|---------|
| `data/dmv_macro_baselines.csv` | Manual / BLS | Base input data: wages, housing, benefit caps by jurisdiction and year |
| `data/political/fec_funding_profiles.json` | `fec_integration_v251d.py` | Cycle-filtered (2024) funding profiles with corruption flags |
| `data/political/fec_excluded_self_funding.json` | `fec_integration_v251d.py` | Excluded contributions (self-funding, multi-cycle, transfers) |
| `data/political/fec_quick_results.json` | `fec_quick_test.py` | Diagnostic test — **multi-cycle, NOT a data source** |
| `data/political/employer_contribution_gap.json` | `employer_contribution_gap.py` | Per-state gap: frozen base vs. expected wage-indexed base |
| `data/political/political_layer_report.json` | `political_layer_builder.py` | Congress.gov members enriched with Census median income + committees |
| `data/political/fec_audit_log.json` | `api_client.py` | All API calls with status, timestamps, and cache hits |

### Figures (13 PNGs) + 11 Interactive Charts + County Map

| File | Description |
|------|-------------|
| `figures/01_bai_decay_trajectory.png` | BAI decay 2010–2026 — all three jurisdictions crossing below 1.0 |
| `figures/02_wbi_stagnation.png` | WBI stagnation — wage base as share of average wage, frozen while wages rise |
| `figures/03_mipi_clawback.png` | MIPI clawback severity — penalty rate on supplementary earnings |
| `figures/04_housing_vs_wba_gap.png` | Housing cost vs. benefit gap — weekly survival deficit by state |
| `figures/05_employer_per_employee_gap.png` | Per-employee underpayment ($84–$157/worker/year) |
| `figures/06_employer_aggregate_gap.png` | Annual trust fund shortfall ($601.3M/year across DMV) |
| `figures/07_statutory_vs_expected_wage_base.png` | Statutory vs. expected wage base — what employers would pay if the base tracked wages |
| `figures/08_real_value_index.png` | Real Value Index — frozen benefits vs. inflation-adjusted 2026 value (MD ~$306, VA ~$244, DC ~$335) |
| `figures/09_unemployment_context.png` | Unemployment rate trends + federal UI spending — who is exposed |
| `figures/10_spending_accountability.png` | Scatter: employer campaign money vs. federal UI investment per lawmaker's state |
| `figures/11_fec_total_receipts.png` | FEC total receipts by member |
| `figures/12_fec_business_vs_labor.png` | Business vs. labor contributions — committee chairs skew heavily business |
| `figures/13_fec_contribution_mix.png` | Contribution mix by category (100% stacked) |

All 13 figures are also available as interactive Plotly charts in `interactive/` (11 files) and embedded in `index.html` behind a toggle button. The county choropleth map is at `maps/dmv_counties.html`.

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | This file |
| `DATA_CATALOG.md` | Full file inventory with lineage map and metadata standard |
| `ENVIRONMENT_ARCHITECTURE.md` | Future architecture proposal (not yet implemented) |
| `Slicers_and_Drilldown_Strategy.md` | Interactive dashboard design specification (not yet implemented) |
| `index.html` | Portfolio landing page — embeds all 10 figures with methodology notes |
| `.env.example` | API key template (copy to `.env` and fill in your keys) |
| `requirements.txt` | Python dependencies |

### CI/CD

| File | Purpose |
|------|---------|
| `.github/workflows/validate.yml` | Validates JSON, CSV, figures (13 PNGs), script syntax, and runs `pytest tests/ -v` on every push/PR |
| `.github/workflows/data_refresh.yml` | Monthly cron (1st of month, 06:00 UTC) — fetches live data from all 6 APIs, regenerates all figures and charts, auto-commits |

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
- **Aggregate trust fund shortfall:** **$601.3M/year** across DMV (using DOL historical effective SUI rates)
  - Virginia: $252.4M/year
  - Maryland: $248.6M/year
  - DC: $100.3M/year
- **Wage base erosion:** MD base is now 11.7% of average wage (down from 16.3% in 2010); VA 11.7% (down from 16.7%); DC 8.0% (down from 13.6%)

### Political Accountability: Who Funds the Freeze
- **7 members** with UI-relevant committee assignments analyzed using FEC 2023–2024 reporting period data
- **$89.9M** in total committee activity; once David Trone's $62.9M in *verified candidate self-loans* are correctly removed, **$27.0M** is true outside money
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

Sources: [MD Compensation Commission 2026](https://mgaleg.maryland.gov/Pubs/Other/2026-Report-of-the-General-Assembly-Compensation-Commission.pdf) · [CRS RL30064 Congressional Salaries](https://www.congress.gov/crs-product/RL30064) · [WSET VA 278% raise](https://wset.com/news/local/virginia-senate-democrats-pass-state-budget-add-nearly-300-percent-pay-increase-for-legislators-money-taxes-richmond-republicans-amendments-affordability) · [DC Code §1-611.09](https://code.dccouncil.gov/us/dc/council/code/sections/1-611.09)

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

### 3. Generate the base analysis

```bash
python -m ui_index.core_engine
python tools/generate_figures.py
```

### 4. Generate the employer contribution gap

```bash
python -m ui_index.employer_models
python tools/generate_employer_gap_charts.py
```

### 5. Generate the political funding layer

```bash
python -m ui_index.fec_pipelines
python tools/generate_fec_charts.py
python -m ui_index.political_layer_builder
```

### 6. Run the delta analysis (corruption detection)

```bash
python -m ui_index.delta_analyzer
```

---

## 🔧 Data Provenance

Every JSON data file includes a `_metadata` block documenting:
- **Generated by:** Which script produced it
- **Generated at:** Timestamp
- **Cycle:** Election year (for FEC data) or analysis year
- **Data sources:** BLS QCEW, BLS LAUS, USDOL, HUD FMR, FEC, Census ACS, Congress.gov, USASpending.gov, FRED (St. Louis Fed — independent inflation cross-validator)
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

---

## ⚠️ Known Limitations

- **Campaign finance categorization** uses keyword matching on contributor names (approximate). For production use, official FEC committee IDs should be used.
- **Business/labor categorization** is based on string patterns, not official industry codes.
- **Self-funding detection** uses last-name matching and may include false positives.
- **Avg wages and covered employment** in the employer gap are approximate BLS estimates.
- **The employer gap methodology** uses the 2010-ratio approach (Method B). Alternative methodologies (full wage base, CPI-only, national peer average, wage growth index) would produce different dollar figures. See the source code for scenario definitions.

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

- [BAI/WBI/MIPI Analysis](https://nbviewer.org/github/thedatavigilante/UI_INDEX/blob/main/ui_index_analysis.ipynb)
- [Political Layer Analysis](https://nbviewer.org/github/thedatavigilante/UI_INDEX/blob/main/political_layer_analysis.ipynb)

---

## 🔗 Repository

https://github.com/thedatavigilante/UI_INDEX

---

*Built for policymakers, journalists, and anyone who believes a safety net should actually catch people.*
