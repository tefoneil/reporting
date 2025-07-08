# Directory Organization

This document explains the clean directory structure for the Monthly Reporting system.

## Main Directories

### `/final_output/` 
**Purpose**: Official reports generated via GUI
- Contains production-ready reports
- Only files generated through the GUI interface
- Default output location for GUI (configured in GUI layout)
- These are the "real" reports for business use

### `/test_outputs/`
**Purpose**: CLI testing and development outputs  
- All CLI test runs (`python monthly_reporting_cli.py --output test_outputs/test_name`)
- Development/debugging outputs
- Version testing (v0.1.9 hotfixes, etc.)
- Not for production use

### `/archive_old_versions/`
**Purpose**: Historical versions and deprecated work
- Old directory structures from previous development
- Legacy test outputs
- Deprecated code versions
- Anything no longer actively used

## Files Organization

### Root Directory (Clean)
Contains only:
- Core Python files (`*.py`)
- Documentation (`*.md`)
- Configuration files (`requirements.txt`, etc.)
- Essential folders (`docs/`, `tests/`)

### No Output Files in Root
- All `*.docx`, `*.txt`, `*.json` output files are in organized directories
- No loose charts/ directories
- No temporary test files

## Usage Guidelines

1. **GUI Users**: Always outputs to `/final_output/` automatically
2. **CLI Testing**: Use `--output test_outputs/your_test_name` 
3. **Archive Policy**: Move old test directories to `/archive_old_versions/` periodically

## Current Status (July 2025)

- ✅ Moved all June v0.1.9 test outputs to `/test_outputs/`
- ✅ Moved August/July premature tests to `/test_outputs/`  
- ✅ Cleaned root directory of loose output files
- ✅ GUI configured to use `/final_output/` by default
- ✅ Old archive moved to `/archive_old_versions/`

This organization ensures clear separation between production reports and development testing.