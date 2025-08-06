# Monthly Chronic Circuit Report Generation Guide

## Overview
The Monthly Chronic Circuit Reports require data from **two separate Tableau dashboards** to generate complete analysis including circuit identification, performance metrics, and trend analysis.

## Required Input Files

### 1. **Impacts File (Performance Metrics)**
- **Source:** Tableau Dashboard - "Demo for External Analysis"
- **Example:** `Impacts by CI Type Crosstab (2) (1).xlsx`
- **Contains:**
  - Distinct count of incidents (ticket volumes)
  - Circuit availability percentages
  - Cost to serve calculations
  - Outage duration summaries
  - All aggregated performance metrics by circuit

### 2. **Counts File (Chronic Identification)**
- **Source:** Tableau Dashboard - "AssetChronic and VendorCredit"
- **Example:** `Count Months Chronic (1).xlsx`
- **Contains:**
  - COUNTD Months column (tracks months with incidents)
  - Circuit identifiers
  - Used to identify NEW chronic circuits (3-month rule)

## Data Flow

```
Tableau Dashboard 1 (AssetChronic)     Tableau Dashboard 2 (External Analysis)
        |                                           |
        v                                           v
Count Months Chronic.xlsx              Impacts by CI Type Crosstab.xlsx
        |                                           |
        +-------------------+----------------------+
                            |
                            v
                    Monthly Builder Script
                            |
                            v
                    Generated Reports:
                    - Chronic_Circuit_Report_[Month]_[Year].docx
                    - Chronic_Corner_[Month]_[Year].docx
                    - chronic_summary_[Month]_[Year].json
                    - Performance charts (PNG files)
```

## Key Business Logic

1. **Chronic Definition:** Circuits appearing in 3 consecutive months
2. **New Chronic Detection:** Circuits reaching their 3rd month in the reporting period
3. **Performance Analysis:** Top/bottom performers by:
   - Ticket volume (e.g., 50 tickets for circuit SR216187)
   - Cost impact
   - Availability percentage
   - Mean Time Between Failures (MTBF)

## Usage Examples

### GUI Method (Recommended)
1. Open Ops Toolkit GUI
2. Navigate to **Monthly Reporting** tab
3. Select **Impacts File (Performance Metrics)**: Choose your impacts file
4. Select **Counts File (Chronic Identification)**: Choose your counts file
5. Set output directory (optional)
6. Click **Run Monthly Report**

### Command Line Method
```bash
python modules/monthly_reporting/monthly_builder.py \
  --impacts "Impacts by CI Type Crosstab (2) (1).xlsx" \
  --counts "Count Months Chronic (1).xlsx" \
  --output ./reports \
  --show-indicators
```

Or using the unified CLI:
```bash
python ops_toolkit.py monthly \
  --impacts "Impacts by CI Type Crosstab (2) (1).xlsx" \
  --counts "Count Months Chronic (1).xlsx" \
  --output ./reports
```

## Required Column Headers

### Impacts File Must Contain:
- `Config Item Name` (or `Configuration Item Name`)
- `Outage Duration`
- Additional recommended: `Distinct count of Inc Nbr`, `Inc Resolved At (Month / Year)`

### Counts File Must Contain:
- `Config Item Name` (or `Configuration Item Name`)
- `COUNTD Months`
- Additional recommended: `Incident Network-facing Impacted CI Type`

## File Format Support
- **Excel files:** `.xlsx`, `.xls`
- **CSV files:** `.csv`
- **Column aliasing:** `Configuration Item Name` automatically becomes `Config Item Name`

## Sample Output Metrics

From a typical monthly report:
- **Total Chronic Circuits:** 23
- **New Chronics This Month:** 1 (circuit 444282783)
- **Total Incidents Analyzed:** 117 circuits with 599 total tickets
- **Worst Performer:** SR216187 with 50 tickets in the period
- **Highest Cost Impact:** PTH TOK EPL 90030025 at $26,324
- **Lowest Availability:** PTH TOK EPL 90030025 at 79.98%

## Troubleshooting

### Common Errors and Solutions

**"Missing required column 'Config Item Name'"**
- Ensure your file has either `Config Item Name` or `Configuration Item Name`
- Check for trailing spaces in column headers

**"Missing required column 'Outage Duration'"**
- Verify the impacts file contains outage duration data
- Check exact spelling and capitalization

**"Missing required column 'COUNTD Months'"**
- Ensure the counts file is from the correct Tableau dashboard
- Verify the column exists and isn't renamed

### File Validation
The system automatically validates:
- File existence and readability
- Required column presence
- Column name aliasing (Configuration Item Name → Config Item Name)
- Data type compatibility

## Best Practices

1. **File timing matters** - For May 2025 reports, use Feb-April data (3 months = chronic threshold)
2. **Aggregation level** - Ensure Tableau exports are at circuit level, not individual incident level
3. **Consistent naming** - Use descriptive filenames with date ranges
4. **Data freshness** - Use the most recent Tableau exports for accurate analysis
5. **Backup originals** - Keep copies of source files before processing

## Integration Notes

- **Auto-open reports:** Enable in GUI settings to automatically open generated documents
- **Output organization:** Reports saved to `./reports/monthly/` by default
- **Format consistency:** All outputs follow standardized naming conventions
- **Cross-platform:** Works on Windows, macOS, and Linux

This two-dashboard approach ensures complete visibility into both chronic circuit identification and their operational impact, providing comprehensive monthly reporting for network operations teams.