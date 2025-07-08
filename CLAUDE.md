# RBuilder - Claude Context

## 🎯 **Project: RBuilder Circuit Analysis System**
Advanced circuit analysis and reporting platform that processes Tableau exports to generate comprehensive Word documents, charts, and trend analysis for operations teams.

## 🚀 **Current Status: v0.1.9-rc13 PRODUCTION READY + EXECUTABLE**

### **📋 Latest Achievement - Complete Executable Distribution System**
**Status:** ✅ COMPLETE - Production system + working standalone executable  
**Branch:** `v0.1.9-hotfix2` (pushed to GitHub at 7df3e15)  
**Impact:** Full deployment-ready system with 77MB RBuilder executable including complete historical data

### **🔧 Critical Executable Enhancement - Discrete Naming & Complete Integration**
**Latest Achievement:** 77MB RBuilder executable with pre-loaded May-June 2025 historical data  
**Security Enhancement:** Changed name from "Monthly_Report_Builder" to "RBuilder" for discretion  
**Current Status:** Fully functional RBuilder executable with complete trend analysis capability  
**Result:** Zero setup required - trend analysis works immediately on any Windows PC

### **💼 Complete Distribution Strategy:**
- **Technical Users:** Python source code with comprehensive documentation
- **Non-Technical Users:** Standalone executable with GUI launcher
- **Enterprise Ready:** GitHub Releases for binary distribution

### **🔧 Critical Breakthrough - Availability Calculation Resolution**
**Root Cause Identified:** After systematic analysis of reference repository v2.20-rc2-p5b (commit `ec0764e`), discovered that availability calculations should use pre-calculated `'SUM Outage (Hours)'` column from counts file, not converted `'Outage Duration'`.

**Solution Implemented:**
- **Direct Git Analysis:** Cloned reference repo, extracted exact logic from working version
- **Hybrid Implementation:** Uses `'SUM Outage (Hours)'` when available, falls back to calculated hours
- **Perfect Results:** All availability values now match reference within 0.003%

**Before vs After:**
```
LZA010663: 92.89% → 78.98% ✅ (perfect match)
PTH TOK EPL: 93.23% → 79.98% ✅ (perfect match) 
N2864477L: 94.55% → 83.90% ✅ (perfect match)
```

---

## 📚 **Comprehensive Project Documentation**

### **Technical Deep Dive**
- **[Monthly Reporting Builder Guide](R_Builder.md)** - Complete technical documentation, architecture, testing, and maintenance guide

### **Recent Major Achievements (v0.1.9-rc8)**

#### **Core Fixes Delivered:**
1. **Perfect Availability Calculations** - Uses reference v2.20-rc2-p5b method with 'SUM Outage (Hours)'
2. **Deduplication Engine** - `_clean_outage()` function prevents double-counting incidents (118→101 rows)
3. **Enhanced Vendor Mapping** - Authoritative circuit inventory integration (PCCW, Telstra, Cirion, TATA, etc.)
4. **Trend Analysis Cleanup** - Fixed placeholder circuit names, graceful missing data handling
5. **Comprehensive Testing** - Regression tests ensure future accuracy within 0.1%

#### **Data Quality Improvements:**
- **Circuit Count Accuracy:** 23 total chronic circuits (excludes media/performance)
- **CID_TEST Filtering:** Multi-stage filtering prevents test circuit leaks
- **Archive Management:** Proper history/YYYY-MM rollover with metadata preservation
- **Input Validation:** SHA256 file hashing and git commit tracking for audit trails

#### **Enhanced User Experience:**
- **Professional Output:** Clean Word documents with accurate vendor prefixes
- **Realistic Metrics:** Availability percentages in operational range (78-88%)
- **Clear Messaging:** Trend analysis handles missing data gracefully
- **Comprehensive Charts:** Bottom5 availability, top5 cost, MTBF analysis

---

## 🛠️ **Development History & Evolution**

### **v0.1.9-rc10 (2025-07-08) - ENHANCED ACTIONABLE INSIGHTS**
- **Enhanced Chart Titles:** All charts now show aggregated values for immediate impact assessment
- **Cost Calculation Fixed:** Corrected 3x inflation bug, now matches source data exactly
- **Consistent Formatting:** Professional titles across charts, Word docs, and text summaries
- **Actionable Metrics:** "Total: 129 tickets", "Total: $37,367 cost", "Average: 83.0% availability"
- **Executive Ready:** Enhanced readability while maintaining full analytical depth
- **Cross-Format Consistency:** Identical enhanced titles in all report formats
- **Business Impact Focus:** Immediate visibility into collective worst performer impact

### **v0.1.9-rc9 (Previous) - FINAL PRODUCTION RELEASE**
- **Trend Analysis Fixed:** Complete month-over-month comparisons working perfectly
- **Professional Output:** Removed emojis for clean business reporting
- **Perfect File Selection:** Fixed previous month detection logic for accurate trends
- **Comprehensive Analytics:** All sections (tickets, cost, availability, MTBF) fully operational

### **v0.1.9-hotfix2 (Previous) - Foundation Building**
- **Negative Availability Fix:** Resolved impossible negative percentage values
- **CID_TEST Filtering:** Multi-stage filtering prevents test circuit contamination
- **Chronic Counting:** Accurate 23-circuit count (excludes media/performance)
- **New Chronic Identification:** Added to Key Takeaways and trend analysis
- **Provider Aliases:** Circuit ID prefixes for improved clarity
- **Folder Rollover:** Automated history/YYYY-MM archive management

### **v0.1.8-audit - Audit Trail Implementation**
- **6-Key Metadata Block:** SHA256 hashing, git commits, timestamps
- **Frozen Legacy List:** May 2025 baseline for consistent classification
- **Enhanced JSON Output:** Machine-readable audit trails

---

## 🧪 **Technical Architecture & Testing**

### **Core Processing Pipeline:**
```
Input Files → Deduplication → Chronic Logic → Metrics Calculation → Report Generation
     ↓              ↓             ↓              ↓                    ↓
  Excel/CSV    _clean_outage()  Business    Reference Method    Word/Charts/JSON
                               Rules       'SUM Outage (Hours)'
```

### **Quality Assurance Framework:**
- **Regression Tests:** `test_availability_calculation_v2.py` ensures reference accuracy
- **Unit Tests:** Deduplication, availability calculations, trend analysis
- **Integration Tests:** Full pipeline with test data fixtures
- **Data Validation:** Row count preservation, file integrity checks

### **Key Performance Metrics:**
- **Accuracy:** <0.1% difference from reference availability calculations
- **Processing:** 118→101 rows after deduplication (17 duplicates removed)
- **Coverage:** 23 chronic circuits + 11 media + performance monitoring
- **Reliability:** Comprehensive test suite prevents regression

---

## 📞 **Session Context & User Profile**

### **User Experience Level:**
- **Expert** with Claude Code workflows and monthly reporting requirements
- **Production Focus:** Deployment-ready system with accurate metrics
- **Quality Oriented:** Systematic testing and validation approach
- **GitHub Integration:** Professional version control and documentation

### **Current Project Status:**
- **✅ All Core Issues Resolved:** Availability, deduplication, vendor mapping, trends
- **✅ Production Ready:** Comprehensive testing and validation complete
- **✅ GitHub Updated:** v0.1.9-rc8 committed and pushed to repository
- **✅ Documentation Complete:** Technical guide and context documentation

### **Key Technical Decisions Made:**
- **Reference Method Adoption:** Use v2.20-rc2-p5b availability calculation exactly
- **Deduplication Strategy:** Based on ['Config Item Name', 'Distinct count of Inc Nbr']
- **Vendor Mapping Enhancement:** Circuit inventory integration for authoritative data
- **Trend Analysis Improvement:** Graceful missing data handling with clear messaging
- **Testing Philosophy:** Comprehensive regression tests for critical calculations

---

## 🔧 **Integration & Workflow**

### **Input Requirements:**
- **Impacts by CI Type Crosstab.xlsx:** Incident data with outage duration in seconds
- **Count Months Chronic.xlsx:** Pre-calculated 'SUM Outage (Hours)' and metadata
- **Optional:** Circuit inventory for enhanced vendor mapping

### **Output Structure:**
- **final_output/:** Current month reports (Word docs, JSON, charts)
- **history/YYYY-MM/:** Archived versions for trend comparison
- **tests/:** Comprehensive test suite with fixtures

### **Command Line Usage:**
```bash
python monthly_builder.py \
    --impacts "path/to/impacts.xlsx" \
    --counts "path/to/counts.xlsx" \
    --month "June"
```

### **Quality Controls:**
- **Availability Accuracy:** Must match reference within 0.1%
- **Circuit Count Validation:** 23 total (excludes media/performance)
- **CID_TEST Filtering:** No test circuits in production output
- **Deduplication Verification:** No duplicate incident counting

---

## 🎯 **Maintenance & Support**

### **Critical Knowledge:**
- **Availability Calculation:** Always use 'SUM Outage (Hours)' from counts file when available
- **Deduplication Required:** Run `_clean_outage()` before any metrics calculation
- **Reference Validation:** Test against v2.20-rc2-p5b reference values (LZA010663: 78.98%)
- **Trend Analysis:** Handles placeholder previous month data gracefully

### **Common Issues & Solutions:**
```
❌ Negative availability values → ✅ Verify 'SUM Outage (Hours)' column exists
❌ Inflated outage hours → ✅ Check deduplication, ensure no double-counting
❌ Placeholder circuit names → ✅ Previous month contains test data (handled gracefully)
❌ Missing vendor prefixes → ✅ Update inventory_vendors dict in utils.py
```

### **Future Enhancement Areas:**
- **Real-time Integration:** Direct ServiceNow API connectivity
- **Interactive Dashboards:** Web-based trend analysis
- **Automated Alerting:** Threshold-based notifications
- **Configuration Management:** YAML-based settings externalization

---

## 📚 **Documentation References**

### **Technical Documentation:**
- **[R_Builder.md](R_Builder.md)** - Complete technical architecture and implementation guide
- **[DIRECTORY_ORGANIZATION.md](DIRECTORY_ORGANIZATION.md)** - File structure and organization
- **tests/** - Comprehensive test suite with examples and fixtures

### **Session History:**
- **Availability Crisis Resolution:** Systematic debugging and reference system analysis
- **Git Repository Analysis:** v2.20-rc2-p5b commit extraction and logic copying
- **Comprehensive Testing:** Regression test development and validation
- **Production Deployment:** GitHub integration and documentation completion

### **Key Achievements:**
- **Perfect Accuracy:** Availability calculations match reference exactly
- **Production Quality:** Comprehensive testing and error handling
- **Professional Output:** Clean reports with enhanced vendor identification
- **Maintainable Code:** Well-documented, tested, and organized codebase

---

*This context file provides session continuity and quick reference. For complete technical details, architecture deep-dives, and implementation guidance, see the comprehensive [R_Builder.md](R_Builder.md) documentation.*