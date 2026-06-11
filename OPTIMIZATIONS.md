<!-- markdownlint-disable -->

# Master Optimization List — The Stagnant Safety Net

**Running log of every audit, correction, and enhancement since project inception.**
Numbered with sub-items for traceability. Status: ✅ done · 🔄 in progress · 📋 planned

Last revised: 2026-06-11

---

## Phase 3 — Portfolio Hardening (✅ complete, commit `dac9d4c`)

1. ✅ **Buy Me a Coffee integration** — 4 placements (nav, hero section, footer callout, footer link)
2. ✅ **LinkedIn byline** — `linkedin.com/in/sierran` in nav and footer
3. ✅ **Light/dark mode toggle** — `body.light` CSS class, localStorage persisted
4. ✅ **"So What?" callouts** — plain-language `.callout-plain` boxes opening each chapter
5. ✅ **README corrections** — aligned figures with narrative

## Phase 4 — Live-Source Data Audit (✅ complete, commit `fa6e5ec`)

6. ✅ **Virginia Max WBA correction** — $378 → $430 (VEC SB 1056, eff. Jan 4 2026)
   - 6.1 ✅ VA BAI recalculated 0.90 → 1.02
   - 6.2 ✅ VA stat-box reflagged danger/red → lime ↑ SB1056
   - 6.3 ✅ Ch1 + Ch3 narrative reframed to "barely above, first fix since 2014"
7. ✅ **DC Avg Annual Wage correction** — $95,000 → $112,400 (BLS QCEW, internal consistency)
8. ✅ **FEC total correction** — $46.6M (stale) → $89.9M actual ($26.1M ex-Trone)
9. ✅ **David Trone disclosure** — Total Wine & More (~$2.4B), Ways & Means, 98.7% self-funded
10. ✅ **Warner/Van Hollen off-cycle disclosure** — not 2024 candidates (2026/2028 races)
11. ✅ **Notebook 1 overhaul** (`ui_index_analysis.ipynb`) — exec summary, data validation cell, 4 investigative takes, cross-index synthesis
12. ✅ **Notebook 2 overhaul** (`political_layer_analysis.ipynb`) — exec summary, B:L ratio cell, conflict matrix, investigative narrative
13. ✅ **README verification footnotes** — 6 live-source URLs
14. ✅ **Lawmaker salary research** — MD +12.5% vs UI +0%; VA +278% vs UI +13.8% (sourced)

## Phase 5 — UX/UI Site Architecture (🔄 in progress)

15. ✅ **Investigative-take blockquotes on index.html** — 4 chart-anchored takes (BAI, WBI, MIPI, Housing Gap) + lawmaker take, crimson-bordered `.investigative-take` style
16. ✅ **Cross-Index Severity Banner** — 3-col grid (DC CRITICAL / MD SEVERE / VA CAUTIONARY)
17. ✅ **Lawmaker Salary vs. UI Benefit table on index.html** — 4-row contrast (MD/VA/DC/Congress) with sourced links
18. ✅ **Navigation upgrade** — added Political Layer / Methodology / About cross-page links
19. ✅ **index.html methodology section** trimmed to summary + link (full content moved to methodology.html)
20. ✅ **political.html** — full political layer page: exec brief, 4-section FEC comparison matrix, Trone profile, lawmaker deep-dive, methodology disclosure
21. ✅ **methodology.html** — data validation table, formulas, housing cost note, limitations
22. ✅ **about.html** — bio, what I built, fractional CDO offer, hire me

## Phase 6 — FEC Methodology Corrections (📋 planned, root cause confirmed 2026-06-11)

23. 📋 **Self-funding detection fix** — replace last-name substring matching with FEC loan transaction types (`15C/16C/15E/16E`). Currently over-excludes Kaine ($9.5M), Warner ($5.9M), Hoyer ($2.6M) — these are joint-committee transfers, not personal loans. Only Trone has true candidate self-loans.
24. 📋 **Conduit/memo-code filter** — add `if c.get('memo_code'): continue` in Schedule A loop to drop pass-through contributions inflating Hoyer/Cline/Ruppersberger business totals.
25. 📋 **B:L categorization via committee_type** — replace name-keyword matching (0–30% coverage) with FEC PAC `committee_type` field (L=labor, B=business) for defensible ratios.
26. 📋 **Vendor exclusion from business** — CROWDWAVE CAMPAIGNS, NEW BLUE INTERACTIVE, etc. are political vendors mis-tagged as corporate donors; exclude from business total.
27. 📋 **Election-cycle normalization** — add per-month fundraising rate to normalize off-cycle (Warner 2026, Van Hollen 2028) vs. active 2024 candidates.
28. ✅ **4-section comparison matrix design** — Raw Receipts / True Self-Fund Corrected / Verified B:L / Per-Month Normalized (built into political.html as honest interim view pending script fixes).
29. 📋 **Fix `total` NameError** — `analyze_member` references undefined `total` at line ~285 (should be `receipts`).

## Phase 7 — Data Governance (🔄 in progress, audit complete 2026-06-11)

30. 📋 **employer_contribution_gap.json metadata wrapper** — bare list violates the `{_metadata, data}` standard; wrap in `employer_contribution_gap.py`.
31. 📋 **Figure numbering convention** — document slots 08–10 reserved for CPI/real-value charts; new charts start at 14.
32. 📋 **Script rename** — `fec_integration_v251d.py` → `fec_integration.py` (drop version suffix; git tracks versions).
33. 📋 **Data placement** — move `employer_contribution_gap.json` out of `data/political/` (it is economic, not political data).
34. ✅ **DATA_CATALOG.md** — added rows for the 4 portfolio pages + OPTIMIZATIONS.md; documented figure numbering convention (08–10 reserved).
35. ✅ **.gitignore verified** — correctly excludes `.env`, `.venv`, `__pycache__`; re-includes `figures/*.png`.

---

*Maintained by The Data Vigilante (Sierra Napier, MPA). This file is the single source of truth for what has changed and what remains.*
