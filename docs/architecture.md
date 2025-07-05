# Monthly Reporting Architecture

## Overview

The Monthly Reporting module is a standalone tool for generating chronic circuit analysis reports from Tableau export data. It processes Excel/CSV files containing circuit performance data and generates comprehensive Word documents, charts, and summaries.

## Core Components

### 1. ChronicReportBuilder (`monthly_builder.py`)
Main processing engine that handles:
- Data loading and validation from Excel/CSV files
- Chronic circuit logic and classification
- Performance metrics calculation
- Report generation (Word, PDF, charts)

### 2. CLI Interface (`monthly_reporting_cli.py`)
Command-line interface providing:
- File validation and error handling
- Progress tracking with tqdm
- Configurable logging (debug/quiet modes)
- Dry-run capability for testing

### 3. Data Analyzer (`analyze_data.py`)
Utility for exploring Excel file structure and sample data viewing.

## Data Flow

```
Input Files (Excel/CSV)
    ↓
Data Loading & Validation
    ↓
Chronic Circuit Logic Processing
    ↓
Performance Metrics Calculation
    ↓
Chart Generation (matplotlib/seaborn)
    ↓
Report Generation (Word documents)
    ↓
Output Files
```

## Input Requirements

### Impacts File
Required columns:
- `Config Item Name` - Circuit identifier
- `Incident Network-facing Impacted CI Type` - Provider/vendor
- `Outage Duration` - Outage time in seconds
- `SUM Outage (Hours)` - Total outage hours
- `Cost to Serve (Sum Impact x $60/hr)` - Financial impact
- `Distinct count of Inc Nbr` - Number of incidents

### Counts File
Required columns:
- `Config Item Name` - Circuit identifier
- `COUNTD Months` - Number of months with incidents

## Output Files

### Generated Reports
1. **Chronic Corner** (`Chronic_Corner_[month].docx`) - Executive summary format
2. **Circuit Report** (`Chronic_Circuit_Report_[month].docx`) - Detailed analysis
3. **Text Summary** (`chronic_circuits_list_[month].txt`) - Plain text listing
4. **Data Export** (`chronic_summary_[month].json`) - Machine-readable data

### Charts (PNG format)
- Top 5 circuits by ticket volume
- Top 5 circuits by cost to serve
- Bottom 5 circuits by availability
- Bottom 5 circuits by MTBF

## Business Logic

### Chronic Circuit Classification
- **Chronic Consistent**: Circuits with consistent performance issues
- **Chronic Inconsistent**: Circuits with sporadic but significant issues  
- **Media Chronics**: Media service circuits requiring special handling
- **Performance Monitoring**: Circuits under 30/60-day observation

### New Chronic Detection
- Circuits reaching 3rd month of incidents
- Must have completed 60-day → 30-day monitoring progression
- Excludes regional circuits (if `--exclude-regional` flag used)
- Filters out name variations of existing chronics

### Regional Circuit Handling
Configurable exclusion of circuits identified as regional:
- Cirion circuits: 500335805, 500332738, etc.
- Globenet circuits: IST6022E#2_010G, IST6041E#3_010G
- Other regional identifiers as defined in business rules

## Configuration Options

### CLI Parameters
- `--exclude-regional`: Exclude regional circuits from new chronic detection
- `--show-indicators`: Add (C)hronic and (R)egional flags to circuit names
- `--debug`: Enable verbose logging and error traces
- `--quiet`: Suppress progress bars and reduce output
- `--dry-run`: Validate inputs without generating files

### Indicator System
When `--show-indicators` is enabled:
- `(C)` = Circuit is in chronic list
- `(R)` = Circuit is identified as regional
- `(C/R)` = Circuit is both chronic and regional

## Error Handling

### File Validation
- Checks file existence and readability
- Validates file format (Excel/CSV)
- Provides user-friendly error messages

### Processing Errors
- Graceful handling of missing columns
- Data type conversion with error recovery
- Comprehensive logging for debugging

### Exit Codes
- `0`: Success
- `1`: File not found or access error
- `2`: Processing or validation error

## Dependencies

### Core Libraries
- `pandas`: Data processing and Excel I/O
- `numpy`: Numerical calculations
- `matplotlib/seaborn`: Chart generation
- `python-docx`: Word document creation
- `openpyxl`: Excel file support

### CLI Enhancement
- `tqdm`: Progress bars
- `argparse`: Command-line interface
- `logging`: Error tracking and debugging

### GUI Support (Optional)
- `FreeSimpleGUI`: Graphical interface integration

## Testing

### Smoke Test (`tests/smoke_test.sh`)
Validates:
- CLI help functionality
- Dry-run operation
- Full report generation
- Output file creation
- File size verification

### Sample Data
Synthetic test files with representative circuit data for development and CI/CD.

## Future Enhancements

### Planned Features
- Additional output formats (PDF, Excel)
- Custom business rule configuration
- Enhanced chart customization
- API interface for programmatic access

### Integration Opportunities
- Tableau direct integration
- ServiceNow API connectivity
- Automated scheduling and delivery
- Dashboard integration