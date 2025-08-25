# GOLDEN ARCHIVE - IMMUTABLE HISTORICAL DATA

## ⚠️ CRITICAL: DO NOT MODIFY FILES IN THIS DIRECTORY ⚠️

This directory contains the authoritative, immutable historical chronic circuit data.
These files serve as the permanent record and baseline for all trend analysis.

## Archive Structure

```
golden_archive/
├── 2025-05_May/       # May 2025 chronic data (baseline)
├── 2025-06_June/      # June 2025 chronic data
└── 2025-07_July/      # July 2025 chronic data
```

## File Contents

Each month directory contains:
- `chronic_circuits_list.txt` - Human-readable chronic circuit list
- `chronic_summary.json` - Complete JSON data with metrics
- `CHECKSUM.sha256` - SHA256 checksums for verification

## Verification

To verify archive integrity, run:
```bash
python3 archive_guardian.py --verify
```

## Protection Mechanisms

1. **Git Protection**: `.gitattributes` marks these as binary files
2. **Checksums**: SHA256 hashes verify file integrity
3. **Archive Guardian**: Script monitors and reports any changes
4. **Documentation**: This README serves as the policy document

## Data Timeline

- **May 2025**: Initial baseline, 24 chronic circuits (8 consistent, 15 inconsistent)
- **June 2025**: 24 chronic circuits maintained
- **July 2025**: 28 chronic circuits (24 + 4 new)
- **August 2025**: To be generated (pending)
- **September 2025**: To be generated (pending)

## Usage Policy

1. **READ ONLY**: These files are for reference only
2. **No Edits**: Never modify these files directly
3. **New Reports**: Generate new reports in `/final_output/`
4. **Trend Analysis**: Use these as the authoritative baseline

## Recovery

If files are accidentally modified:
1. Check git history: `git log -- golden_archive/`
2. Restore from git: `git checkout HEAD -- golden_archive/`
3. Verify checksums: `python3 archive_guardian.py --verify`

---
*Archive created: August 25, 2025*
*Purpose: Preserve chronic circuit historical data*
*Maintainer: Reporting Team*