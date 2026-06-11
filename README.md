<!-- markdownlint-disable -->

# ⚖️ The Stagnant Safety Net

<p align="center">
  <img src="https://github.com/thedatavigilante.png" width="120" alt="The Data Vigilante Logo">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/build-passing-success?style=flat-square" alt="Build Status">
  <img src="https://img.shields.io/badge/Data%20Validation-Verified-blue?style=flat-square" alt="Data Validation">
  <img src="https://img.shields.io/badge/Version-1.0.0--Production-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-orange?style=flat-square" alt="License">
</p>

> ***A forensic data portfolio exposing how inflation, frozen policies, and political campaign contributions have been systematically weaponized to weaken unemployment insurance across the DMV.***

**Architected by:** Sierra Napier, MPA ([The Data Vigilante](https://github.com/thedatavigilante))  
**Target Focus:** District of Columbia, Maryland, Virginia (DMV) Legislative Auditing

---

## 🗺️ What This Is

This repository houses the end-to-end data pipeline, economic modeling, and forensic analysis behind an investigation into the systemic erosion of unemployment insurance (UI) safety nets across the DMV (District of Columbia, Maryland, and Virginia). 

For decades, the conversation around unemployment has been dominated by administrative hand-waving and the myth of "trust fund insolvency." This project cuts through the noise. By marrying live-source macroeconomic indicators with campaign finance records from the Federal Election Commission ([FEC.gov](https://www.fec.gov)), this portfolio transitions the narrative from personal frustration to undeniable structural proof: **the safety net is failing because it was designed to fail.**

### 🛠️ The Architecture at a Glance
To prove this decay, the codebase dynamically pulls, caches, and models data across two primary layers:

* **The Macroeconomic Layer:** Calculates four custom socio-economic vulnerability indices (BAI, WBI, MIPI, and the Housing Gap) anchored against historical baselines (2010, 2018, 2026) to expose exactly how far benefits have fallen behind real-world survival costs.
* **The Political Accountability Layer:** Pipelines 2024 election cycle fundraising metrics to cross-reference the lawmakers holding crucial committee oversight seats against the corporate PAC money funding their campaigns.

The entire ecosystem compiles seamlessly into an automated, responsive **4-page static portfolio site** designed to give journalists, policymakers, and advocates the raw, unvarnished data infrastructure needed to demand structural legislative transparency.

---

## 📐 Forensic Metrics Defined

To prove exactly how the system shifts the economic burden onto working families, this engine calculates four core macroeconomic indices. We use raw, un-gameable figures from the Bureau of Labor Statistics (BLS) and the U.S. Census Bureau to turn personal frustration into undeniable structural proof.

### 1. Benefit Adequacy Index (BAI)
`BAI = Max_WBA ÷ Weekly_Housing_Cost`

$$\text{BAI} = \frac{\text{Maximum Weekly Benefit Amount (WBA)}}{\text{Weekly Housing Cost}}$$

* **Current Baseline Rule:** Isolates whether the maximum weekly benefit cap forces a choice between rent and immediate survival. **Any BAI < 1.0 indicates systemic failure** — the benefit does not cover housing alone.
* **The Human Reality (Why it matters):** Can your unemployment check secure a roof over your head? A score of **1.0** means your check covers rent and baseline utilities *only*, leaving exactly $0.00 for food, medicine, or transit. When a state legally mandates a BAI below 1.0 (as seen in DC and Maryland), it forces a structural housing crisis on a worker the exact day they are laid off.

### 2. Regressive Wage Base Index (WBI)
`WBI = Taxable_Wage_Base ÷ Avg_Annual_Wage`

$$\text{WBI} = \frac{\text{Taxable Wage Base}}{\text{Average Annual Wage}}$$

* **Current Baseline Rule:** Tracks how much of the average worker's wage is actually subject to unemployment insurance taxation. As wages rise and the wage base stays frozen, the WBI falls — meaning employers pay into a shrinking share of the wage pool, narrowing the trust fund.
* **The Human Reality (Why it matters):** This measures how heavily the funding rules favor massive corporations at the expense of regular workers. As regional salaries grow, the tax cap remains frozen. Big businesses pay taxes on a smaller and smaller fraction of their payroll, starving the public trust fund of hundreds of millions of dollars. This artificial scarcity is then used by politicians as a hollow excuse to deny you an inflation adjustment.

### 3. Multi-Income Penalty Index (MIPI)
`MIPI = (Side_Hustle_Earnings − Disregard_Threshold) ÷ Max_WBA`

$$\text{MIPI} = \frac{\text{Side Hustle Earnings} - \text{Disregard Threshold}}{\text{Maximum Weekly Benefit Amount (WBA)}}$$

* **Current Baseline Rule:** Quantifies the institutional penalty on workers who earn supplementary income while receiving benefits. High MIPI = aggressive clawback that punishes resourcefulness and traps workers in dependency.
* **The Human Reality (Why it matters):** If you try to survive a layoff by picking up part-time gig work or a freelance side hustle to buy groceries, the system aggressively penalizes you. States allow a tiny, stagnant "Earnings Disregard" (often as low as $30 a week), but every single dollar you earn *above* that threshold is slashed **dollar-for-dollar** from your check. It acts as a 100% effective tax rate on survival.

### 4. Housing Gap
`Housing_Gap = Weekly_Housing_Cost − Max_WBA`

$$\text{Housing Gap} = \text{Weekly Housing Cost} - \text{Maximum Weekly Benefit Amount (WBA)}$$

* **Current Baseline Rule:** Measures the raw weekly financial deficit facing an unemployed individual before buying a single bag of groceries.
* **The Human Reality (Why it matters):** This isn't an abstract data point—it is the brutal, cold weekly dollar shortage you are forced to figure out just to keep from being evicted before you can even think about buying groceries, paying a medical bill, or filling up your gas tank to get to an interview.

## 📦 The Evidence Locker (Data Artifacts & Visual Proof)

Data isn't just rows and columns; it’s the verifiable proof behind our findings. Below is the structured index of the underlying datasets and the generated visual portfolio built by this engine.

## 📦 The Evidence Locker (Data Artifacts & Visual Proof)

Data isn't just rows and columns; it’s the verifiable proof behind our findings. Below is the structured index of the underlying datasets and the generated visual portfolio built by this engine to provide an undeniable receipt of how the system operates.

### 📊 Forensic Notebooks
| File | Tactical Purpose | What it Exposes to the Common Person |
| :--- | :--- | :--- |
| `ui_index_analysis.ipynb` | Interactive Macro Auditing | **The Baseline Sandbox.** The actual analytical space where the multi-decade decay of the BAI, WBI, and Housing Gaps were calculated using raw economic data. |
| `political_layer_analysis.ipynb` | Campaign Finance Cross-Examination | **The Corruption Blueprint.** Connects incoming FEC donation streams directly to committee assignments, proving that oversight isn't neutral. |

### 🗄️ Processed Evidence (Data Files)
| File / Dataset | Core Source Engine | What the Data Discovered (The Real-World Meaning) |
| :--- | :--- | :--- |
| `data/dmv_macro_baselines.csv` | Manual / BLS / Census | **The Bedrock Truth.** The raw, unvarnished numbers tracking weekly housing costs, average annual wages, and statutory benefit caps since 2010. |
| `data/political/fec_funding_profiles.json` | `fec_integration_v251d.py` | **The Money Trail.** Cycle-filtered campaign profiles for targeted lawmakers, stamped with corporate PAC dependency flags to show who pays for the stagnation. |
| `data/political/fec_excluded_self_funding.json` | `fec_integration_v251d.py` | **The Out-of-Bounds Ledger.** Isolates massive self-funders (like David Trone's $62.9M run) so multi-millionaire anomalies don't distort traditional corporate PAC benchmarks. |
| `data/political/employer_contribution_gap.json` | `employer_contribution_gap.py` | **The Deficit Receipt.** Computes the exact state-by-state dollar amount missing from public trust funds due to frozen corporate tax bases ($601.3M aggregate shortfall). |
| `data/political/political_layer_report.json` | `political_layer_builder.py` | **The Accountability Matrix.** Fuses active Congress members with their specific committee power seats and regional household income baselines. |

### 📉 Visual Portfolio (Generated Tracking Figures)
These exported visualization assets are dynamically embedded directly into the frontend user interface to turn dense datasets into immediate visual realization.

* **`figures/01_bai_decay_trajectory.png`** : *The Breaking Point.* Universally tracks the downward slide of the BAI from 2010 to 2026 as it crosses below the 1.0 survival threshold across DC, MD, and VA—proving the system no longer covers basic survival.
* **`figures/02_wbi_stagnation.png`** : *The Corporate Free Ride.* Charts how the taxable wage base shrinks as a percentage of real wages, starving public trust funds while regional productivity and corporate profits climb.
* **`figures/03_mipi_clawback.png`** : *The Side-Hustle Poverty Trap.* Visually graphs the immediate financial cliff workers hit when trying to supplement an unlivable check with part-time work—exposing the literal dollar-for-dollar penalty state systems impose on resourcefulness.
* **`figures/06_employer_aggregate_gap.png`** : *The $601.3 Million Hole.* A stark bar chart totaling the immense funding gap left in state safety nets by stagnant employer tax policies, showing the money that *should* be supporting families.
* **`figures/12_fec_business_vs_labor.png`** : *The Influence Skew.* Contrasts the lopsided ratio of business-to-labor PAC money flowing into the campaigns of key oversight committee chairs, demonstrating exactly why worker protections are frozen.

---

---
### Notebooks (2 files)

| File | Purpose |
|------|---------|
| `ui_index_analysis.ipynb` | BAI/WBI/MIPI/Housing Gap analysis — interactive exploration |
| `political_layer_analysis.ipynb` | Political funding + committee analysis — interactive exploration |

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

### Figures (10 PNGs)

| File | Description |
|------|-------------|
| `figures/01_bai_decay_trajectory.png` | BAI decay 2010–2026 — all three jurisdictions crossing below 1.0 |
| `figures/02_wbi_stagnation.png` | WBI stagnation — wage base as share of average wage, frozen while wages rise |
| `figures/03_mipi_clawback.png` | MIPI clawback severity — penalty rate on supplementary earnings |
| `figures/04_housing_vs_wba_gap.png` | Housing cost vs. benefit gap — weekly survival deficit by state |
| `figures/05_employer_per_employee_gap.png` | Per-employee underpayment ($84–$157/worker/year) |
| `figures/06_employer_aggregate_gap.png` | Annual trust fund shortfall ($601.3M/year across DMV) |
| `figures/07_statutory_vs_expected_wage_base.png` | Statutory vs. expected wage base — what employers would pay if the base tracked wages |
| `figures/11_fec_total_receipts.png` | FEC total receipts by member |
| `figures/12_fec_business_vs_labor.png` | Business vs. labor contributions — committee chairs skew heavily business |
| `figures/13_fec_contribution_mix.png` | Contribution mix by category |

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
- **Aggregate trust fund shortfall:** **$601.3M/year** across DMV (using DOL historical effective SUI rates)
  - Virginia: $252.4M/year
  - Maryland: $248.6M/year
  - DC: $100.3M/year
- **Wage base erosion:** MD base is now 11.7% of average wage (down from 16.3% in 2010); VA 11.7% (down from 16.7%); DC 8.0% (down from 13.6%)

### Political Accountability: Who Funds the Freeze
- **7 members** with UI-relevant committee assignments analyzed using FEC 2023-2024 reporting period data
- **$89.9M** in total committee activity; once David Trone's $62.9M in *verified candidate self-loans* are correctly removed, **$21.7M** is true outside money
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
python ui_index_engine.py
python generate_figures.py
```

### 4. Generate the employer contribution gap

```bash
python employer_contribution_gap.py
python generate_employer_gap_charts.py
```

### 5. Generate the political funding layer

```bash
python fec_integration_v251d.py
python generate_fec_charts.py
python political_layer_builder.py
```

### 6. Run the delta analysis (corruption detection)

```bash
python delta_analyzer.py
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
