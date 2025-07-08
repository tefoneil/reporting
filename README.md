# RBuilder - Circuit Reporting System

## 📋 **Overview**
Automated circuit reporting system that processes Tableau exports and generates professional Word documents for business operations.

## 🎯 **Choose Your Version**

### **📥 For Non-Technical Users: Download Executable**
**No Python installation required!** Just download and double-click:

👉 **[Download Latest Release](https://github.com/tefoneil/reporting/releases)**

- **Windows:** Download `RBuilder.exe`
- **Mac:** Download `RBuilder`
- See **[📖 User Guide](README_EXECUTABLE.md)** for complete instructions

### **💻 For Developers: Python Source**
Clone repository and run from source code (requires Python installation).

---

## 🚀 **Quick Start (Python Version)**

### **Step 1: Get Your Data Files**
Download these 2 files from Tableau each month:
- **Impacts Crosstab** (Excel format)
- **Count Months Chronic** (Excel format)

### **Step 2: Launch the GUI**
```bash
python monthly_builder.py
```

### **Step 3: Use the Interface**
1. **Browse** for your Impacts Crosstab and Count Months Chronic files
2. **Configure** options (exclude regional, show indicators)
3. **Select** report month and year
4. **Generate Report** and watch the progress

### **Step 4: Get Your Reports**
Find your generated reports in `./final_output/`:
- `Chronic_Corner_[Month]_[Year].docx` - Executive presentation format
- `Chronic_Circuit_Report_[Month]_[Year].docx` - Detailed analysis report
- `chronic_circuits_list_[Month]_[Year].txt` - Quick reference text summary
- Charts folder with 4 PNG files
- JSON data summary

**Note:** The default output directory is `./final_output` within the monthly_reporting folder.

## ⚙️ **Installation**
```bash
pip install pandas numpy python-docx matplotlib seaborn openpyxl
```

## 🛠 **GUI Options**

The graphical interface provides:
- **File Selection**: Browse for your Impacts and Counts files
- **Report Settings**: Choose month, year, and output directory
- **Processing Options**: 
  - Exclude regional circuits from new chronic detection
  - Show (C) and (R) flags in reports
- **Progress Monitoring**: Real-time log of processing steps

*(CLI options available for testing - see `monthly_reporting_cli.py --help`)*

## 📁 **Files**
- `monthly_builder.py` - Main reporting script with GUI interface
- `analyze_data.py` - Data analysis utilities
- `monthly_reporting_cli.py` - CLI wrapper for testing
- `README.md` - This file

## 📊 **What Gets Generated**

### **Chronic Corner Report:**
- Special formatted 4-column metric block
- Vendor breakdown tables (Consistent/Inconsistent/Media)
- Performance monitoring section
- Charts with legend at bottom

### **Circuit Report:**
- Executive-ready summary with key takeaways
- Professional styled metric table (64 circuits tracked)
- Top/Bottom 5 analysis with performance data
- Recommendations section
- Visual charts

### **Supporting Files:**
- 4 performance charts (PNG format)
- Complete data export (JSON format)
- PDF conversion (if LibreOffice available)
- **NEW:** Text summary with chronic circuit lists (easy reference)

## 🔧 **Monthly Workflow**

### **For Each Month:**
1. **Download** new Tableau exports
2. **Update** file paths in command
3. **Run** the script
4. **Review** generated reports
5. **Deliver** for COB deadline

## 📝 **Usage Examples**

### **GUI Mode (Recommended)**
```bash
# Launch the graphical interface
python monthly_builder.py
```

### **CLI Mode (Testing Only)**
```bash
# Basic monthly run
python monthly_reporting_cli.py --impacts "data.xlsx" --counts "counts.xlsx"

# With indicators and custom output
python monthly_reporting_cli.py \
  --impacts "impacts.xlsx" \
  --counts "counts.xlsx" \
  --output ./reports \
  --show-indicators

# Clean run without regional indicators
python monthly_reporting_cli.py \
  --impacts "impacts.xlsx" \
  --counts "counts.xlsx" \
  --exclude-regional
```

---

## ✨ **Enhanced Features (v0.1.9-rc13)**

### **🎯 Enhanced Chart Titles with Aggregated Insights**
Charts now show immediate actionable metrics:
- **"Top 5 by Ticket Volume - Total: 129"** (collective impact)
- **"Top 5 by Cost to Serve - Total: $37,367"** (budget exposure)
- **"Top 5 by Worst Availability - Average: 83.0%"** (performance baseline)

### **💰 Accurate Cost Calculations**
- Fixed critical 3x inflation bug
- All costs now match source data exactly
- Example: LZA010663 now shows $9,215 (was incorrectly $27,645)

### **📊 Complete Trend Analysis**
- Working month-over-month comparisons
- New problem circuits vs improvements identified
- Strategic recommendations with emerging patterns

### **🎨 Professional Output**
- Consistent enhanced titles across all formats (charts, Word docs, text)
- Executive-ready insights with collective impact metrics
- Clean formatting suitable for business presentations

---

## 🔧 **For Developers**

### **Building Executable:**
See **[📖 Build Instructions](BUILD_INSTRUCTIONS.md)** for creating standalone executables.

### **Project Structure:**
- **Source Code:** Complete Python implementation
- **Documentation:** Technical guides and user manuals  
- **Build System:** PyInstaller configuration for distribution
- **Testing:** Comprehensive test suite for accuracy validation

---

*RBuilder v0.1.9-rc13 | Complete executable distribution system for operations teams*