# Changelog

All notable changes to this project will be documented here.

## [1.0.0] - 2025-11-04
### Added
- Automated **monthly** GitHub Action to rebuild PDF + export Tableau assets.
- Excel artifacts in `04_Excel/`:
  - `KPI_Snapshot.xlsx` (with Last Updated UTC)
  - `01_Data_Overview.xlsx` (Summary, Columns, Data_Quality, Refresh_Log)
  - `Dashboard_Notes.xlsx` (Dashboard_Notes, KPI_Definitions, Links)
- Report footer shows **Last refreshed (UTC)** on every page.

### Improved
- Robust KPI extraction (CSV/XLSX tolerant, resilient headers).
- PowerShell script `scripts/update_all.ps1` to rebuild + push artifacts.

### Fixed
- Git merge issues on binary assets by enforcing `.gitattributes`.
