# Slicers and Drilldown Strategy

## Interactive Dashboard Specification

### Core Slicers (User Controls)

| Slicer | Type | Options | Default |
|--------|------|---------|---------|
| **Jurisdiction** | Multi-select | DC, MD, VA | All |
| **Year** | Slider | 2010, 2018, 2026 | 2026 |
| **Index Type** | Radio | BAI, WBI, MIPI | BAI |
| **Member Chamber** | Multi-select | House, Senate, DC Delegate | All |
| **Committee Filter** | Multi-select | Ways & Means, Finance, Budget, Appropriations, Labor, HELP | All |
| **Party** | Multi-select | Democratic, Republican | All |
| **Income Range** | Range slider | $0 - $200,000 | Full range |

### Drilldown Hierarchy

```
Dashboard (3 states, 3 indices, 3 years)
├── Click Jurisdiction → Jurisdiction Detail Page
│   ├── State-level BAI/WBI/MIPI trends (2010-2026)
│   ├── County-level income distribution (Census ACS)
│   └── District-level member profiles
├── Click Member → Member Profile Card
│   ├── Constituent median income (Census)
│   ├── Committee assignments (Congress.gov)
│   ├── FEC funding profile (business vs labor contributions)
│   └── Top contributor industries (when OpenSecrets available)
├── Click Index Value → Index Explanation Modal
│   ├── Formula breakdown
│   ├── Data sources
│   └── Comparison to national benchmark
└── Click Year → Timeline View
    ├── All indices for selected year
    ├── Legislative events (SUI cap changes, UI benefit updates)
    └── Campaign finance peaks (FEC data)
```

### Chart Interactions

| Chart | Click Action | Drilldown Target |
|-------|-------------|------------------|
| BAI Decay Trajectory | Click bar | Jurisdiction detail with county map |
| WBI Stagnation | Click line point | Year-specific employer gap analysis |
| MIPI Clawback | Click bar | Part-time earnings scenario calculator |
| Housing vs WBA | Click gap bar | Rent burden by county (Census S2503) |
| Constituent Income | Click district | Member profile card |
| Committee Members | Click member | FEC funding profile + contributor list |
| FEC Receipts | Click bar | Schedule A itemized contributions table |
| Business vs Labor | Click segment | Industry-coded contributor breakdown |

### Implementation Stack

**Option A: Streamlit (Fastest)**
- Pros: Pure Python, 1-click deploy, native widgets
- Cons: Less customizable, slower with large datasets
- Deploy: Streamlit Cloud or self-hosted

**Option B: Plotly Dash**
- Pros: Full React control, callbacks, professional look
- Cons: More complex, needs heroku/self-host

**Option C: ObservableHQ + GitHub Pages**
- Pros: Free, hosted, interactive JS
- Cons: Data needs to be static JSON, not real-time API

**Recommended:** ObservableHQ for the portfolio page (static JSON exports), Streamlit for live dashboard (API-connected).

### Data Export for ObservableHQ

```python
# Export all data as static JSON for ObservableHQ
{
  "dmv_baselines": [...],           # from dmv_macro_baselines.csv
  "member_profiles": [...],         # from political_layer_report.json
  "fec_profiles": [...],            # from fec_funding_profiles.json
  "employer_gaps": [...],           # from employer_contribution_gap.json
  "census_income": [...],           # from Census API cache
  "index_metadata": {               # formulas and thresholds
    "bai": {"formula": "...", "threshold": 1.0, "description": "..."},
    "wbi": {"formula": "...", "threshold": 0.15, "description": "..."},
    "mipi": {"formula": "...", "threshold": 0.5, "description": "..."}
  }
}
```

### Next Steps

1. [ ] Generate `dashboard_data.json` — consolidated export for ObservableHQ
2. [ ] Build ObservableHQ notebook with all slicers and drilldowns
3. [ ] Embed ObservableHQ iframe in gosidehustlesisi.github.io portfolio page
4. [ ] Build Streamlit live version (connects to Census + FEC APIs)
5. [ ] Add hover tooltips with data source citations
