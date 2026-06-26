# Next Stage Roadmap — Phase 6: Data Expansion & API Integration

**Status:** 📋 Planned | **Target:** Post-PR-merge | **Priority:** Medium-High

This document captures the additional free APIs identified during the optimization research that were not integrated into the current portfolio scope. The 5-phase optimization (visibility, community health, SEO, social proof) was intentionally scoped to portfolio hardening, not data expansion. These APIs represent the next phase of analytical depth.

---

## APIs Researched but Not Yet Integrated

| API | Data Provided | Why It Matters | Integration Complexity | Priority |
|-----|-------------|---------------|----------------------|----------|
| **BEA Regional Price Parities (RPP)** | State/metro cost-of-living index beyond housing | True COL-adjusted BAI: current BAI uses housing only; RPP captures food, transport, healthcare, childcare | Medium: BEA API v1, JSON output, annual release | 🔴 High |
| **MIT Living Wage Calculator** | Living wage by county (family composition adjusted) | Compare UI benefit to actual living wage, not just housing; exposes how far benefits fall from survival | Medium: Static CSV/Excel downloads, no API; requires manual refresh | 🔴 High |
| **C2ER Cost of Living Index** | Quarterly COL index by metro area (100 = national avg) | Multi-factor COL index for DMV metros; independent validation of HUD FMR approach | Low-Medium: Limited free tier; requires registration | 🟡 Medium |
| **Census SAIPE** | Small Area Income & Poverty Estimates by county | Poverty context for county choropleth; overlap between UI claimants and poverty line | Low: Census API, same key as ACS; JSON output | 🟡 Medium |
| **USDA SNAP/FNS** | SNAP participation rates, benefit adequacy by state | Safety net overlap: how many UI claimants also need SNAP; total welfare gap | Low: USDA data portal, CSV downloads | 🟡 Medium |
| **BJS Justice Stats** | Incarceration/unemployment correlation | Criminal justice system's impact on unemployment duration and benefit access | Medium: BJS data portal, periodic reports | 🟢 Low |
| **SAMHSA** | Substance abuse/mental health service gaps by state | Mental health safety net gaps alongside UI decay | Low: SAMHSA data portal, annual reports | 🟢 Low |

---

## Recommended Integration Order

### Phase 6A: BEA RPP + MIT Living Wage (Highest Impact)

**Goal:** Create a **Cost-of-Living Adjusted BAI (COL-BAI)** that captures the full survival basket, not just housing.

**Steps:**
1. Create `fetch_bea_rpp.py` — BEA API v1, regional price parities by state/metro
   - Endpoint: `https://apps.bea.gov/api/data?UserID={KEY}&method=GetData&datasetname=Regional&TableName=MAPPING&GeoFIPS=XX&Year=ALL&ResultFormat=json`
   - Parse: `RPP_All` (all items), `RPP_Goods`, `RPP_Services`, `RPP_Rents`
   - Save: `data/bea_rpp.json` with metadata wrapper

2. Create `fetch_mit_living_wage.py` — MIT Living Wage Calculator scraper/CSV parser
   - Source: `https://livingwage.mit.edu/` (state/county pages)
   - Extract: Living wage for 1 adult, 2 adults + 1 child, 2 adults + 2 children
   - Save: `data/mit_living_wage.json` with metadata wrapper

3. Create `col_bai_engine.py` — new index engine
   - `COL_BAI = Max_WBA ÷ (Weekly_Housing_Cost × RPP_All/100)`
   - `Living_Wage_Gap = MIT_Living_Wage − Max_WBA`
   - Output: `data/col_bai_results.json`

4. Create `generate_col_bai_figure.py` — new figure (Figure 14)
   - Multi-panel: COL-BAI vs. BAI by jurisdiction; Living Wage Gap; RPP-adjusted housing cost
   - Save: `figures/14_col_bai_comparison.png`

5. Update `index.html` — add COL-BAI section between Chapter 3 (MIPI) and Chapter 4 (Trust Fund)
6. Update `methodology.html` — document COL-BAI formula and housing cost methodology note
7. Update `README.md` — add COL-BAI to metrics table and file inventory

**Estimated effort:** 2–3 days
**Dependencies:** BEA API key (free registration)

---

### Phase 6B: Census SAIPE + USDA SNAP (Safety Net Overlap)

**Goal:** Show the overlap between UI decay and other safety net programs.

**Steps:**
1. Create `fetch_census_saipe.py` — SAIPE poverty estimates by county
   - Endpoint: `https://api.census.gov/data/timeseries/poverty/saipe` (or SAIPE bulk files)
   - Extract: Poverty rate, median income, poverty count for DC/MD/VA counties
   - Save: `data/census_saipe.json`

2. Create `fetch_usda_snap.py` — SNAP participation rates by state
   - Source: USDA FNS data portal
   - Extract: SNAP participants, benefit adequacy, Thrifty Food Plan gap
   - Save: `data/usda_snap.json`

3. Create `safety_net_overlap_analysis.py` — cross-reference UI + SNAP + poverty data
   - Question: what % of UI claimants are also SNAP-eligible?
   - Question: what's the combined safety net gap?
   - Output: `data/safety_net_overlap.json`

4. Create `generate_safety_net_figure.py` — new figure (Figure 15)
   - Save: `figures/15_safety_net_overlap.png`

5. Update `index.html` — add safety net overlap section (new chapter or appendix)

**Estimated effort:** 1–2 days
**Dependencies:** None (Census API key already available)

---

### Phase 6C: C2ER COL Index (Independent Validation)

**Goal:** Independent validation of the HUD FMR housing cost methodology.

**Steps:**
1. Create `fetch_c2er_coli.py` — C2ER Cost of Living Index (free registration)
   - Source: `https://www.c2er.org/` (quarterly index by metro)
   - Extract: Composite index for Washington DC, Baltimore, Richmond metros
   - Save: `data/c2er_coli.json`

2. Create `housing_cost_validation.py` — compare HUD FMR vs. C2ER vs. BEA RPP
   - Output: `data/housing_cost_validation.json`
   - Document: which housing cost method produces the most conservative BAI

3. Update `methodology.html` — add housing cost validation table with three methods

**Estimated effort:** 1 day
**Dependencies:** C2ER free registration

---

### Phase 6D: BJS + SAMHSA (Justice & Health Overlap)

**Goal:** Document the criminal justice and mental health dimensions of UI policy.

**Steps:**
1. Create `fetch_bjs_justice.py` — incarceration rates by state
2. Create `fetch_samhsa_gaps.py` — mental health service availability by state
3. Create `generate_justice_health_figure.py` — new figure (Figure 16)
4. Update `index.html` — add justice/health context as appendix or sidebar

**Estimated effort:** 2–3 days
**Priority:** Low (contextual, not core to the financial audit)

---

## Integration Architecture

```
New fetch scripts (6 total):
├── fetch_bea_rpp.py          → data/bea_rpp.json
├── fetch_mit_living_wage.py  → data/mit_living_wage.json
├── fetch_census_saipe.py     → data/census_saipe.json
├── fetch_usda_snap.py        → data/usda_snap.json
├── fetch_c2er_coli.py        → data/c2er_coli.json
├── fetch_bjs_justice.py      → data/bjs_justice.json
├── fetch_samhsa_gaps.py      → data/samhsa_gaps.json

New analysis scripts (3 total):
├── col_bai_engine.py         → data/col_bai_results.json
├── safety_net_overlap.py     → data/safety_net_overlap.json
├── housing_cost_validation.py → data/housing_cost_validation.json

New figures (3 total):
├── figures/14_col_bai_comparison.png
├── figures/15_safety_net_overlap.png
├── figures/16_justice_health_context.png

Updated pages:
├── index.html        (add COL-BAI chapter, safety net overlap appendix)
├── methodology.html  (add COL-BAI formula, housing validation table)
├── README.md        (add new metrics, new files, new sources)
```

---

## Data Governance Notes

- **Metadata standard:** Every new JSON file must include the `{_metadata, data}` wrapper with `generated_by`, `generated_at`, `sources`, `methodology`, and `caveat` fields.
- **Live-source verification:** New APIs must be validated against live sources before inclusion in the portfolio (same standard as existing data).
- **Honest limitations:** Every new index must include a limitations section (same standard as existing BAI/WBI/MIPI).
- **Figure numbering:** Continue from Figure 14 (08–10 are reserved for CPI/real-value charts; 11–13 are FEC; 14+ are new).

---

## Why These Were Deferred

The 5-phase optimization (PR #13) focused exclusively on **portfolio visibility and credibility**: dynamic badges, README structure, community health files, SEO meta tags, and profile README. Adding new data sources would have:

1. Expanded the PR scope beyond the "5/5 GitHub Portfolio Rating" goal
2. Introduced new data validation requirements that would delay merge
3. Required new figure generation and cross-page updates
4. Shifted focus from "making the existing work discoverable" to "making the work deeper"

Both are valid goals, but they are sequential, not parallel. The portfolio is now a 5/5. The data expansion is Phase 6.

---

*Documented 2026-06-25 during the final validation audit of PR #13.*
*Maintained by The Data Vigilante (Sierra Napier, MPA).*
