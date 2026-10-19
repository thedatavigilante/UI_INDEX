# 🧠 OPTIMIZATIONS.md

> A running log of corrections, clarifications, and roadmap items for the `UI_INDEX` project.
> *This is the source of truth for the portfolio's accuracy and its biggest limitations.*

**Current Status:** October 20, 2026 — v54 of Unclaimed Money Command Center synced. BLS September 2026 + LAUS August 2026 integrated.

---

## Recent Corrections (Newest First)

### 52 — October 2026 BLS Data Refresh ✅ INTEGRATED
**Date:** 2026-10-20  
**File:** `README.md`, `DATA_CATALOG.md`, `figures/09_unemployment_context.png`  
**Change:** Integrated BLS September 2026 CPS and BLS LAUS August 2026 data into all relevant files.
- US unemployment rate: **4.2%** (Sep 2026 CPS) — 7.1 million unemployed
- Long-term unemployed: **1.9 million** (27.1% of all unemployed)
- DC unemployment: **5.7%** (Aug 2026 LAUS) — highest in the nation
- MD unemployment: **4.1%** (Aug 2026 LAUS)
- VA unemployment: **3.6%** (Aug 2026 LAUS)
- CPI-U: **3.7%** YoY (Sep 2026)
- Energy CPI: **+20.4%** YoY
- Gasoline: **+34.2%** YoY
- Added "October 2026 Labor Market Reality Check" section to README
- Added "Data Freshness Disclosure" to Methodology section
- Updated verification date badges throughout
- Added 1.9M long-term unemployed stat to 6-Second Scan
**Why it matters:** The previous README referenced BLS data without specifying vintage. The October 2026 refresh anchors all claims to specific BLS releases, making the portfolio auditable and current. The 4.2% "stable" rate is now contextualized against the 1.9M long-term unemployed — a key narrative counterpoint.
**Verification:** [bls.gov/news.release/empsit.nr0.htm](https://www.bls.gov/news.release/empsit.nr0.htm) (CPS Sep 2026) · [bls.gov/lau](https://www.bls.gov/lau/) (LAUS Aug 2026) · [bls.gov/cpi](https://www.bls.gov/cpi/) (CPI Sep 2026)

### 51 — Unclaimed Money Command Center v53 → v54 Sync ✅ INTEGRATED
**Date:** 2026-10-20  
**File:** `README.md` (social links section)  
**Change:** Added "Connect with The Data Vigilante" section with social media placeholder links. GitHub, email, LinkedIn confirmed. TikTok/Instagram/X/YouTube/Substack marked as "launching October 2026."
**Why it matters:** The Data Vigilante brand is launching social media handles in parallel with the October podcast appearance. The README now serves as a canonical link hub.

### 50 — Virginia BAI Updated to 1.02 (SB 1056 Effective Jan 4 2026) ✅ INTEGRATED
**Date:** 2026-06-11  
**File:** `README.md`, `data/dmv_macro_baselines.csv`, `figures/01_bai_decay_trajectory.png`  
**Change:** Virginia max WBA raised from $378 to $430 effective January 4, 2026, per SB 1056. BAI recalculated to 1.02 (from 0.86). Virginia no longer below threshold — now "barely above" at $10/week from failure.
**Verification:** [VEC official announcement](https://vec.virginia.gov/new-weekly-benefit-amounts-effective-january-4-2026)

---

*(Items 1–49 preserved from original OPTIMIZATIONS.md. See repo history for full log.)*

---

## Correction Roadmap — Outstanding

### Phase 6: Methodological Honesty (In Progress)

| # | Item | Status | Notes |
|---|------|--------|-------|
| 23 | FEC business/labor categorization uses keyword matching, not official industry codes | 🟡 DOCUMENTED | Honest in README + political.html four-view matrix |
| 24 | Self-funding detection uses last-name matching with possible false positives | 🟡 DOCUMENTED | Flagged in OPTIMIZATIONS #41 |
| 25 | Mark Warner (VA) + Chris Van Hollen (MD) were not 2024 candidates — figures are off-cycle | 🟡 DOCUMENTED | Added to README Political Accountability section |
| 26 | Lawmaker salary vs. UI benefit contrast table is illustrative, not an accusation of direct causation | 🟡 DOCUMENTED | Explicitly framed as "contrast," not "causation" in README |
| 27 | David Trone's $62.9M in self-loans correctly excluded from outside-money analysis | ✅ VERIFIED | Confirmed against FEC filings + WaPo reporting |
| 28 | Cline (13:1) and Ruppersberger (21:1) are the only members with sufficient B/L coverage for meaningful ratios | ✅ VERIFIED | Others marked "insufficient coverage" |
| 29 | Four-view FEC comparison matrix (raw → adjusted → normalized → normalized + industry) is the honest way to present this data | ✅ IMPLEMENTED | Live on political.html |

### Phase 7: Data Pipeline Automation

| # | Item | Status | Notes |
|---|------|--------|-------|
| 30 | Automate monthly BLS LAUS fetch via GitHub Actions | 🟡 PARTIAL | `data_refresh.yml` exists but needs LAUS API integration |
| 31 | Add "last updated" timestamp badge to all generated figures | 🟡 PARTIAL | README has badge; figures need overlay |
| 32 | Build FRED CPI-U auto-refresh for RVI calculations | 🟡 PLANNED | Currently manual refresh |
| 33 | Add county-level unemployment rate auto-update | 🔴 NOT STARTED | Requires BLS LAUS county API integration |

### Phase 8: October 2026 Refresh Follow-up

| # | Item | Status | Notes |
|---|------|--------|-------|
| 34 | Regenerate Figure 09 (unemployment_context.png) with Aug 2026 LAUS data | 🟡 PENDING | Data updated in README; figure PNG needs re-render |
| 35 | Update Streamlit dashboard with October 2026 stats | 🟡 PENDING | dashboard/app.py needs refresh |
| 36 | Verify HUD FMR 2026 figures for housing cost accuracy | 🟡 PENDING | FMR typically released in late Q3 |
| 37 | Cross-check BLS QCEW 2025 annual averages when released | 🔴 NOT STARTED | QCEW annual data released ~June following year |
| 38 | Add "long-term unemployed" trend line to Figure 09 | 🔴 NOT STARTED | Would strengthen narrative counterpoint |

---

## Style Guide for Future Corrections

When adding a new correction, follow this format:

```markdown
### [NUMBER] — [TITLE] [STATUS]
**Date:** YYYY-MM-DD  
**File:** `filename.ext`  
**Change:** [What changed]  
**Why it matters:** [Why this correction matters]  
**Verification:** [Links to sources]
```

Status markers: `✅ INTEGRATED` | `🟡 PENDING` | `🔴 NOT STARTED` | `🟡 DOCUMENTED`

---

*OPTIMIZATIONS.md — October 20, 2026. Correction log for UI_INDEX forensic data portfolio.*
