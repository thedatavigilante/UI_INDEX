# AUDIT_v1 — Data Pipeline Versioning Matrix
**Branch:** claude/data-source-improvement-ysj9mv | **Audit Date:** 2026-06-15 | **Last updated:** 2026-06-15  
**Scope:** All 13 sections of the portfolio site — data source integrity, pipeline state, open burns

---

## How to Read This Matrix

Each row tracks one site section's **data pipeline health** — whether the right source powers it,
whether the data is live or using a fallback, and what open issues exist.

Individual campaign finance figures (specific candidate receipts, self-funded %, outside money)
are documented in `FEC_COMPARISON.md` with full derivation notes. This matrix tracks structural
integrity only.

**Data State codes:**
- `LIVE` — data comes from a live API call that has run and produced the cache file
- `FALLBACK` — live fetch hasn't run; hardcoded verified values active
- `STATIC` — deliberately static input (CSV, hardcoded reference data)
- `MISSING` — cache file doesn't exist yet; fetch script must run

---

## Versioning Matrix — 13 Sections

| # | Section | Primary Source | Data State | Key Integrity Check | Data Date | Open Burns | Status |
|---|---|---|---|---|---|---|---|
| 1 | HERO / META | — | STATIC | Scope claim "DC/MD/VA 2010–2026" matches CSV date range | 2010–2026 | — | ✅ Clean |
| 2 | CH1 — BAI | `dmv_macro_baselines.csv` | STATIC | MD 0.9556 / VA 1.0238 / DC 0.8538 (computed from 9-row CSV) | 2026 projection | — | ✅ Clean |
| 3 | CH1 — RVI | `data/inflation_crosscheck.json` | **MISSING→FALLBACK** | Hardcoded CPI ratios sourced from FRED; fallback active until `fetch_fred_inflation.py` runs | 2024 CPI | Fetch not yet run | ⚠️ Fallback |
| 4 | CH2 — WBI | `data/political/employer_contribution_gap.json` | STATIC | Wage base ratio: MD 11.7% / VA 11.7% / DC 8.0% (3 records, all > 0) | 2026 | BURN-10 fixed ✅ | ✅ Clean |
| 5 | CH3 — MIPI/Housing | `dmv_macro_baselines.csv` | STATIC | `Weekly_Housing` column present for all 3 states × 3 years (9 rows) | 2026 FMR | — | ✅ Clean |
| 6 | CH4 — Trust Fund | `data/political/employer_contribution_gap.json` | STATIC | Shortfall sum: $601,348,432 (MD $248.6M + VA $252.4M + DC $100.3M) | 2026 | BURN-10 fixed ✅ | ✅ Clean |
| 7 | CH-EXPOSURE | `dmv_macro_baselines.csv` + `data/political/federal_spending.json` | MISSING→FALLBACK | Unemployment rates from BLS LAUS; spending from USASpending fallback | 2024 | Fetch not yet run | ⚠️ Fallback |
| 8 | COUNTY MAP | `maps/dmv_counties.html` (Folium) + `data/us_counties.geojson` | STATIC | GeoJSON loads; DMV subset renders; 3,221 county features in base file | 2023 ACS | — | ✅ Clean |
| 9 | CH5 — FEC | `data/political/fec_funding_profiles.json` | LIVE (2026-06-11) | 7 profiles present / cycle=2024 / all `data_quality: "VALID"` / reconciliation_status: VALIDATED | 2024 cycle | BURN-01 fixed ✅ | ✅ Clean |
| 10 | INTERACTIVE | `interactive/*.html` (11 Plotly files) | STATIC | 11 HTML files present; all load without JS errors | Generated 2026-06 | — | ✅ Clean |
| 11 | LAWMAKERS | Hardcoded (BLS/BEA, state statutes — manually sourced) | STATIC | Salary data cited; VA 183% raise / MD $0 UI raise documented with sources | 2024–2026 | — | ✅ Clean |
| 12 | SOURCES | `methodology.html` data table | STATIC | 11 sources documented; LIVE/VERIFIED/BLOCKED status matches actual fetch results | 2026-06 | — | ✅ Clean |
| 13 | FOOTER | — | STATIC | Date stamp current (Updated: 2026-06-15); data credit line matches active sources | 2026-06-15 | BURN-05/06 fixed ✅ | ✅ Clean |

---

## Pipeline State Summary

| Pipeline Component | State | Blocking? |
|---|---|---|
| `dmv_macro_baselines.csv` (master input) | ✅ Current | No |
| `fec_funding_profiles.json` | ✅ LIVE (2026-06-11) | No |
| `political_layer_report.json` | ✅ LIVE (2026-06-11) | No |
| `employer_contribution_gap.json` | ✅ Calculated (2026-06-11) | No |
| `inflation_crosscheck.json` | ⚠️ MISSING — needs `fetch_fred_inflation.py` + `FRED_API_KEY` | No (fallback active) |
| `sui_rates.json` | ⚠️ MISSING — needs `fetch_dol_sui_rates.py` | No (pytest skips) |
| `county_data.json` | ⚠️ MISSING — needs `fetch_county_data.py` + `CENSUS_API_KEY` | No (GeoJSON fallback) |
| `federal_spending.json` | ⚠️ MISSING — needs `fetch_usaspending.py` | No (hardcoded fallback) |

**4 of 8 data files missing** — all have verified fallbacks. Site renders correctly in current state.
Live fetch requires GitHub Actions run with secrets set, or local run with `.env` populated.

---

## Data Governance State (from 2026-06-14 audit)

| Check | Result |
|---|---|
| JSON metadata wrapper compliance | 5/6 files compliant pre-fix; employer_contribution_gap.json fixed (BURN-10) |
| `reconciliation_status` enum validity | fec_quick_results.json fixed: "DEPRECATED" → "AUDIT" (DG-01) |
| `DATA_CATALOG.md` figure slots current | Fixed: slots 08–10 documented as in-use (DG-06) |
| CI metadata validation | Added to `validate.yml` (DG-07) |
| API retry coverage | fetch_housing.py `_fetch_hud()` and `fetch_census_county_income()` both now have 3-attempt retry with exponential backoff (DG-05 ✅) |
| Fallback logging | `fallback_applied` flag added to fetch_fred_inflation.py, fetch_county_data.py, fetch_usaspending.py (DG-04 ✅); fetch_bls_baselines.py updates CSV not JSON — flag deferred |

---

## Open Items (Deferred — Not Blocking)

| ID | Item | File | Priority |
|---|---|---|---|
| DG-02 | fec_audit_log.json data structure: summary object instead of call-record array | `data/political/fec_audit_log.json` + `api_client.py` | Medium |
| DG-03 | Add `data_sources` field to 4 FEC files | `fec_funding_profiles.json` + 3 others | Low |
| DG-04 | Add `fallback_applied` flag — 3 of 4 done (fred/county/usaspending). fetch_bls_baselines.py writes CSV not JSON | `fetch_bls_baselines.py` | Low |
| DG-08 | Create `datapackage.json` Frictionless Data manifest | Repo root | Low |

---

*This matrix tracks the v1 audit state. Update on next data refresh or major content change.*
