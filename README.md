# Monthly Chronic Circuit Reporting

## 📋 **Overview**
Automated monthly chronic circuit reporting system that processes Tableau exports and generates professional Word documents for COB deadlines.

## 🚀 **Quick Start**

### **Step 1: Get Your Data Files**
Download these 2 files from Tableau each month:
- **Impacts Crosstab** (Excel format)
- **Count Months Chronic** (Excel format)

### **Step 2: Run the Command**
```bash
python monthly_builder.py \
  --impacts "/path/to/impacts_file.xlsx" \
  --counts "/path/to/counts_file.xlsx" \
  --output ./final_output \
  --show-indicators
```

### **Step 3: Get Your Reports**
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

## 🛠 **Command Options**

### **Required:**
- `--impacts` : Path to Tableau impacts Excel file
- `--counts` : Path to Tableau counts Excel file

### **Optional:**
- `--output` : Output directory (default: `./output`)
- `--show-indicators` : Show (C) and (R) flags in reports
- `--exclude-regional` : Exclude regional circuits from new chronic detection
- `--mask-level` : IP masking level (none/partial/alias/remove)

## 📁 **Files**
- `monthly_builder.py` - Main reporting script
- `analyze_data.py` - Data analysis utilities
- `mapping.csv` - Vendor mapping configuration
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
```bash
# Basic monthly run
python monthly_builder.py --impacts "data.xlsx" --counts "counts.xlsx"

# With indicators and custom output
python monthly_builder.py \
  --impacts "impacts.xlsx" \
  --counts "counts.xlsx" \
  --output ./reports \
  --show-indicators

# Clean run without regional indicators
python monthly_builder.py \
  --impacts "impacts.xlsx" \
  --counts "counts.xlsx" \
  --exclude-regional
```