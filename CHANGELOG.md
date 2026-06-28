# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-11

### Added
- Initial release: BAI, WBI, MIPI, Housing Gap indices for DC, MD, VA
- 13 static visualization charts (matplotlib)
- 2 interactive Jupyter notebooks (root level)
- 4 additional notebooks in `/notebooks/` directory (elite stack)
- 4-page GitHub Pages portfolio site (index, political, methodology, about)
- 11 interactive Plotly charts in `/interactive/`
- County-level Folium choropleth map (`maps/dmv_counties.html`)
- Streamlit dashboard with 5 tabs
- Monthly data refresh GitHub Action (`data_refresh.yml`)
- CI/CD validation workflow (`validate.yml`) — pytest + data integrity checks
- FEC API integration with cycle-filtered 2024 data
- Political accountability layer (Congress.gov + Census ACS enrichment)
- Real Value Index (RVI) — inflation-adjusted benefit values
- Cross-index severity assessment banner
- Lawmaker salary vs. UI benefit contrast table

### Data Sources
- BLS QCEW, LAUS, CPI-U
- DOL ETA-5159
- HUD FMR
- FEC API (2024 cycle)
- Census ACS
- Congress.gov
- USASpending.gov
- FRED (St. Louis Fed)
