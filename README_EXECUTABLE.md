# RBuilder - Executable Version

## 🎯 **Quick Start Guide for Non-Technical Users**

This is a standalone executable version of the RBuilder reporting tool. No Python installation or command-line knowledge required!

---

## 📥 **Download & Setup**

### **Step 1: Download the Executable**
1. Go to the [GitHub Releases page](https://github.com/tefoneil/reporting/releases)
2. Download the latest `RBuilder.exe` (or `RBuilder` for Mac)
3. Save it to your Desktop or preferred folder

### **Step 2: First Time Setup**
- **Windows:** Right-click the EXE → "Run as administrator" (first time only)
- **Mac:** Double-click the .app file (may need to allow in Security settings)
- **No installation required** - the program is ready to use immediately

---

## 🖥️ **How to Use**

### **Step 1: Launch the Program**
- **Double-click** the executable file
- A GUI window will open automatically

### **Step 2: Select Your Input Files**
The GUI will show fields for:

**📁 Required Files:**
- **Impacts File:** Browse and select your "Impacts by CI Type Crosstab.xlsx"
- **Counts File:** Browse and select your "Count Months Chronic.xlsx"

**📅 Report Month:**
- Choose the month you're reporting on (e.g., "June")

### **Step 3: Generate Reports**
1. Click the **"Generate Reports"** button
2. Wait for processing (usually 30-60 seconds)
3. Success message will appear when complete

### **Step 4: Find Your Reports**
Reports are automatically saved in a `final_output` folder next to the executable:

**📊 Generated Files:**
- **Chronic_Circuit_Report_[Month].docx** - Detailed analysis
- **Chronic_Corner_[Month].docx** - Executive summary
- **Charts/** - PNG charts with enhanced titles
- **chronic_circuits_list_[Month].txt** - Text summary
- **Monthly_Trend_Analysis_[Month].docx** - Month-over-month comparison

---

## ✨ **Enhanced Features (v0.1.9-rc13)**

### **Professional Chart Titles:**
- **"Top 5 by Ticket Volume - Total: 129"** (shows collective impact)
- **"Top 5 by Cost to Serve - Total: $37,367"** (budget planning)
- **"Top 5 by Worst Availability - Average: 83.0%"** (performance insight)

### **Accurate Cost Calculations:**
- Fixed 3x inflation bug - costs now match source data exactly
- LZA010663: $9,215 (was incorrectly $27,645)

### **Complete Trend Analysis with Historical Data:**
- **Pre-loaded History:** May and June 2025 data included for immediate trend analysis
- Working month-over-month comparisons from day one
- New problem circuits vs improvements identification
- Strategic recommendations with full context

---

## 🔧 **Troubleshooting**

### **"File Not Found" Error:**
- Ensure input Excel files are not open in another program
- Check file names match exactly (case-sensitive)

### **"Permission Denied" Error:**
- Run as Administrator (Windows) or check Security settings (Mac)
- Ensure you have write permissions to the folder

### **Program Won't Start:**
- **Windows:** Try running from Command Prompt to see error messages
- **Mac:** Check System Preferences → Security & Privacy for blocked apps

### **Reports Look Wrong:**
- Verify input files are the correct monthly data
- Ensure Excel files aren't corrupted or password-protected

---

## 📧 **Getting Help**

**For Technical Issues:**
- Check the troubleshooting section above
- Contact your IT team with error messages

**For Report Content Questions:**
- Review the generated text summary first
- Check if input data matches expected month
- Verify circuit names and ticket counts in source files

---

## 📋 **File Size Information**

- **Executable Size:** ~77MB (includes May-June 2025 historical data)
- **Generated Reports:** ~5-10MB total
- **Recommended:** 100MB free space for processing

---

## 🎉 **What Makes This Special**

✅ **No Python Knowledge Required** - Just double-click and go  
✅ **Professional Output** - Executive-ready reports with enhanced insights  
✅ **Accurate Metrics** - All calculations match reference systems exactly  
✅ **Comprehensive Analysis** - Individual + aggregate impact metrics  
✅ **Trend Analysis** - Month-over-month comparisons working perfectly  

---

*RBuilder v0.1.9-rc13 FINAL RELEASE | Standalone executable SHIPPED & READY! 🚀 | For support: contact your Operations team*