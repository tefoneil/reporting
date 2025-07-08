# Data Sources & Column Mappings

## v0.1.8 – Final Data-Source & Availability Rules (approved 2025-07-08)

### 1. Column Mappings

| Workbook                          | Column                    | Purpose |
|----------------------------------|---------------------------|---------|
| Impacts by CI Type Crosstab      | `Distinct count of Inc Nbr` | Ticket totals |
|                                  | `Outage Duration`           | Raw outage minutes |
| Count Months Chronic             | `COUNTD Months`             | Months chronic |

### 2. Canonical ID & Filters

* `canonical_id()` applied to `Config Item Name` before any grouping.
* Rows dropped if `Config Item Name` starts with `CID_TEST` **or** `Vendor` contains "Test".

### 3. Availability Calculation

```
OutageHours  = OutageDuration / 60          # column is minutes
PotentialHrs = DaysInMonth × 24
Availability = 100 × (1 – OutageHours / PotentialHrs)
```

### 4. Safeguards

* If `OutageDuration` already appears to be hours (no value > PotentialHrs×2),
  skip the ÷60 step.
* Banner when >10% non-numeric ticket cells remain.

### 5. Thresholds

* Core chronic thresholds unchanged (tickets ≥ 6, cost ≥ $1 000, availability ≥ 5 pp, MTBF ≥ 0.5 d, rank ≥ 2).
* Trend-analysis thresholds remain in `TREND_THRESH` (tickets ≥ 1, …).

## Implementation Details

### Test Circuit Filtering

The system automatically filters out test circuits in two ways:

1. **Config Item Name Filter**: Any circuit whose name starts with `CID_TEST`
2. **Vendor Filter**: Any circuit whose vendor field contains "Test" (case-insensitive)

This filtering is applied early in the data loading pipeline to ensure test circuits don't affect:
- Chronic circuit classification
- Performance metrics (availability, MTBF)
- Top/Bottom rankings
- Trend analysis

### Smart Unit Detection

The availability calculation includes automatic unit detection:

```python
# Check if any outage value exceeds reasonable hours threshold
max_outage_value = circuit_outages.max()
potential_hours = days_in_period * 24

if max_outage_value > potential_hours * 2:
    # Values are in minutes, convert to hours
    outage_hours = circuit_outages / 60
else:
    # Values appear to be in hours already
    outage_hours = circuit_outages
```

This prevents double-division if the data source team switches from minutes to hours.

### Data Quality Warnings

The system monitors data quality and displays warnings for:

1. **Non-numeric ticket counts**: If >10% of ticket values cannot be converted to numbers
2. **Blank month cells**: If >10% of date fields are empty and require forward-filling

These warnings appear in both CLI and GUI modes to alert users to potential data issues.

## Column Aliases

The system handles common column name variations:

- `Configuration Item Name` → `Config Item Name`
- `Distinct count of Inc Nbr` (preferred for v0.1.8+)
- `SUM Outage (Hours)` (legacy, still supported)
- `Outage Duration` (preferred for v0.1.8+, in minutes)

## Usage Examples

### Environment Variables

```bash
# Core chronic thresholds (unchanged)
export MR_CONSISTENT_THRESHOLD=6
export MR_THRESH_AVAIL_PCT=5.0

# Trend analysis thresholds (separate)
export MR_TREND_TICKETS=1
export MR_TREND_COST_USD=500
export MR_TREND_AVAIL_PCT=2.0
export MR_TREND_MTBF_DAYS=0.2
export MR_TREND_RANK=1
```

### CLI Usage

```bash
python monthly_reporting_cli.py \
  --impacts "Impacts by CI Type Crosstab.xlsx" \
  --counts "Count Months Chronic.xlsx" \
  --output reports/ \
  --month "June 2025"
```

*Document owner: PMA • Revision 1*