# Changelog

All notable changes to the Monthly Reporting project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.9] – 2025-07-08

### Added
- **Production hardening**: Frozen legacy list from May 2025 authoritative baseline
- **Metadata block**: 6-key metadata in JSON output (tool_version, python_version, git_commit, run_timestamp, crosstab_sha256, counts_sha256)
- **Low ticket median warning**: Banner alert when median drops from >1 to ≤1 tickets
- **Comprehensive pytest suite**: 12 tests across 4 test classes validating canonical_id, ticket totals, baseline freeze, and banner warnings
- **SHA256 file hashing**: Audit trail for input data integrity

### Changed
- **Canonical ID function**: Updated with simplified v0.1.9 rules (digits-hyphen-letters suffix trimming)
- **Legacy status loading**: Now uses frozen `docs/frozen_legacy_list.json` as authoritative baseline
- **Utils module**: Extracted shared utilities (canonical_id, warn_low_ticket_median, validate_metadata, get_file_sha256)

### Technical Details
- Frozen legacy list contains 36 circuits (8 consistent, 17 inconsistent, 11 media)
- Git commit tracking for reproducibility
- ISO timestamp format for run metadata
- Cached SHA256 computation for performance
- Pytest fixtures for test data management

## [0.1.8-audit] – 2025-07-08

### Added
- **Audit trail enhancement**: Added `raw_ticket_count_crosstab` field to circuit JSON entries for transparency

## [0.1.8] – 2025-07-08

### Changed
- **Column mappings updated** to use standardized Tableau export columns:
  - Ticket totals: `Distinct count of Inc Nbr` (from impacts crosstab)
  - Outage data: `Outage Duration` (in minutes)
  - Months chronic: `COUNTD Months` (from counts workbook)
- **Test circuit filtering** - automatically excludes:
  - Circuits where `Config Item Name` starts with `CID_TEST`
  - Circuits where `Vendor` contains "Test"
- **Availability calculation** updated to match reference formula:
  - `Availability = 100 × (1 – OutageHours / PotentialHours)`
  - Automatic unit detection: if any outage > (days × 24 × 2), assumes minutes
- **Data quality warnings** added for >10% non-numeric ticket values

### Technical Details
- Smart unit detection prevents double-division if data source switches units
- Test circuit filtering applied early in data pipeline for all metrics
- Availability now correctly uses outage minutes converted to hours
- Data quality banners shown in both CLI and GUI modes

## [0.1.7-b] – 2025-07-08

### Changed
- Lower thresholds apply **only** inside Monthly Trend Analysis 
  (tickets ≥ 1, cost ≥ $500, availability ≥ 2 pp, MTBF ≥ 0.2 days, rank ≥ 1).
- Core chronic thresholds remain: tickets ≥ 6, cost ≥ $1 000, availability ≥ 5 pp, MTBF ≥ 0.5 days, rank ≥ 2.
- Added warning when prior-month summary JSON is missing.

### Technical Details
- New `TREND_THRESH` dict in `analyze_trends.py` with environment variable support:
  - `MR_TREND_TICKETS` (default: 1)
  - `MR_TREND_COST_USD` (default: 500)
  - `MR_TREND_AVAIL_PCT` (default: 2.0)
  - `MR_TREND_MTBF_DAYS` (default: 0.2)
  - `MR_TREND_RANK` (default: 1)
- Core chronic classification logic in `monthly_builder.py` unchanged
- Chronic counts and tables remain stable; only trend analysis shows increased sensitivity

## [0.1.6] – 2025-07-07

### Changed
- **Availability significant change threshold**: Raised from 2% → **5%** to reduce noise in trend analysis
- Added `MR_THRESH_AVAIL_PCT` environment variable for configurable availability threshold
- Other thresholds unchanged: Tickets ≥3, Cost ≥$1,000, MTBF ≥0.5 days, Rank ≥2 positions

### Technical Details
- `AVAIL_THRESH_PCT` constant now controls all availability change detection
- Applied consistently across ranking analysis and strategic insights
- Environment variable allows field tuning without code changes

## [0.1.5-patch1] – 2025-07-07

### Fixed
- **New Chronic promotion lifecycle**: Prior month's "New Chronic" circuits are now automatically evaluated for promotion to Consistent/Inconsistent based on ticket rule (≥6 tickets = Consistent)
- **Dynamic date narrative in Word generation**: Month parameter properly passed to generate accurate "By the end of {month}" text instead of hardcoded dates
- **Baseline hotfix metadata**: Added tracking for promotional logic fixes in JSON output

### Technical Details
- Enhanced `load_baseline_status()` to include prior month's `new_chronics` with `pending_promotion` status
- Added `pending_promotion` handler in classification logic to apply ticket-based promotion rules
- `generate_chronic_corner_word()` now accepts and uses `month_str` parameter for dynamic date narratives
- Version metadata updated to track baseline hotfix implementations

## [0.1.5] – 2025-07-07

### Added
- **Canonical circuit IDs**: Normalize circuit identifiers by extracting first token before `_`, `/`, ` `, or `-` (≥3 digits)
- Ticket counts sourced exclusively from **`Distinct count of Inc Nbr`** column in Count Months Chronic file
- Data quality warning for >10% non-numeric ticket values in GUI
- Comprehensive unit tests for ID normalization and aggregation scenarios

### Fixed
- **Duplicate suffix variations no longer split ticket totals**
- Zero-ticket misclassification for 091NOID circuits resolved through canonical aggregation
- VID- circuits preserved without incorrect splitting (hyphen rule respects ≥3 digits requirement)

### Technical Details
- All baseline legacy IDs converted to canonical form at load-time for consistent lookups
- Circuit variants (e.g., 091NOID1143035717419_889599, 091NOID1143035717419_889621) now aggregate under single canonical ID
- Crosstab file ticket columns ignored to prevent double-counting, only Count Months Chronic used
- Position-based delimiter splitting ensures correct canonical extraction

### Breaking Changes
- Circuit ticket calculations now use canonical IDs, may affect circuits with complex naming variations

## [0.1.4] – 2025-07-07

### Added
- **Hybrid consistency mode**  
  - Legacy Consistent/Inconsistent statuses frozen up to May 2025.  
  - All new chronic circuits use rolling ticket rule (≥ 6 tickets) for status.
- JSON fields: `"version": "0.1.4"`, `"consistency_mode": "hybrid"`.
- Baseline status loader `load_baseline_status()` to read prior summaries.
- GUI warning banner when no prior summaries are found.
- Unit tests for hybrid classification logic and baseline loading.

### Fixed
- Warning banner now fires when no prior summaries are found.

### Technical Details
- Baseline cutover point: May 2025 and earlier summaries freeze circuit status
- New circuits after May 2025 classified by rolling 3-month ticket totals
- Environment variable `MR_CONSISTENT_THRESHOLD` still controls ticket threshold
- Media chronics combine baseline + hardcoded lists (remove duplicates)

## [0.1.3] – 2025-07-07

### Fixed
- **Month / Year forward-fill**: Added  
  `df['Inc Resolved At (Month / Year)'].ffill(inplace=True)`  
  in the data-loader.  
  Prevents rows with blank month cells from being mis-counted as "0 tickets"
  (e.g., 091NOID* circuits in June 2025).

### Added
- Unit test for `get_rolling_ticket_total()` using sample DataFrame with a
  blank month cell.
- Data-quality warning: GUI logs a yellow banner if >10% of month cells
  were blank prior to fill-down.
- Environment variable `MR_DYNAMIC_CONSISTENCY` to toggle between legacy and dynamic modes

### Unchanged
- **Legacy consistency mode** remains the default  
  (`MR_DYNAMIC_CONSISTENCY` environment variable is `0` by default).
- Ticket-based Consistent / Inconsistent logic (≥6 tickets) is available
  but disabled until further notice.

## [0.1.2] – 2025-07-06

### Added
- Severity split: ≥6 tickets → Consistent, else Inconsistent chronic classification
- Environment variable `MR_CONSISTENT_THRESHOLD` for configurable ticket threshold
- JSON fields `rolling_ticket_total`, `status`, and `version` for enhanced auditing
- Rolling ticket calculation helper function `get_rolling_ticket_total()`
- Enhanced smoke test with CID_TEST_7 (7 tickets) and CID_TEST_4 (4 tickets) validation

### Changed
- `process_chronic_logic()` method now applies dynamic classification based on ticket counts
- Chronic circuits are no longer hardcoded as consistent/inconsistent
- JSON output includes circuit-level ticket data for troubleshooting

### Technical Details
- Existing chronic circuits are classified dynamically using rolling 3-month ticket totals
- New chronic detection logic remains unchanged (only affects existing chronics)
- Media chronics remain separate category (not subject to ticket classification)
- Default threshold is 6 tickets but configurable via environment variable

## [0.1.1] – 2025-07-06

### Added
- Baseline logic for chronic circuit promotion from previous month summaries
- Rolling 3-month baseline window for consistent chronic tracking
- Monthly operating procedure documentation

### Changed
- JSON summaries now accumulate in output folder for baseline detection
- Former "New Chronic" circuits automatically promote to "Consistent" status

## [0.1.0] – 2025-07-06

### Added
- GUI-first interface using FreeSimpleGUI
- Smart entry point (GUI if no args, CLI if args provided)
- Real-time progress logging in GUI
- File browser dialogs for input selection
- Month/year selection with current date defaults
- Enhanced error handling and validation

### Changed
- Primary interface is now GUI instead of CLI
- CLI preserved for automated testing and smoke tests
- Updated README to emphasize GUI workflow
- Removed mapping.csv dependency

### Fixed
- Path().lower() bug with proper str() casting
- Month parameter handling for consistent file naming
- Error scope issues in build_monthly_report method

### Documentation
- Added docs/initialization_guide.md with GUI-focused workflow
- Updated README.md for GUI-first approach
- Comprehensive smoke test suite with real data validation