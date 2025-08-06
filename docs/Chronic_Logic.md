# RBuilder Chronic Circuit Classification Logic - Comprehensive Reference

## 🎯 **Overview**
This document serves as the definitive reference for all chronic circuit classification logic in the RBuilder system. It covers every aspect of how circuits are identified, classified, promoted, and managed within the chronic circuit reporting framework.

---

## 📋 **Core Business Rules**

### **1. "Once Chronic, Always Chronic" Principle**
**Fundamental Rule:** Once a circuit becomes chronic, it never automatically drops from the chronic list.

**Implementation:**
- Circuits can only be removed through **manual exclusion** processes
- Historical chronic status is preserved across all monthly reports
- System loads ALL previous chronic circuits from `history/YYYY-MM/` folders
- New monthly data cannot demote existing chronic circuits

**Business Justification:**
- Prevents operational blind spots from temporarily quiet circuits
- Maintains continuity for long-term trend analysis
- Ensures accountability for historically problematic circuits

### **2. 3-Month Persistence Rule** 
**Definition:** A circuit becomes chronic when it appears with incidents in **3 consecutive months**.

**Thresholds:**
- **Month 1:** Circuit enters 60-day performance monitoring
- **Month 2:** Circuit moves to 30-day performance monitoring  
- **Month 3:** Circuit becomes chronic (inconsistent classification)

**Important Notes:**
- Months must be consecutive (gaps reset the counter)
- Any incident activity counts toward persistence
- Classification starts as "inconsistent" regardless of ticket volume

### **3. Consistent vs Inconsistent Classification**
**Classification Threshold:** ≥6 tickets in the current month = Consistent, <6 tickets = Inconsistent

**Rules:**
- **Consistent:** Circuits with ≥6 tickets in current reporting period
- **Inconsistent:** Circuits with <6 tickets in current reporting period
- **Initial Classification:** All new chronic circuits start as "inconsistent"
- **Status Preservation:** Classifications maintained across months unless explicitly changed

---

## 🔄 **Enhanced Promotion Logic (v0.1.9-hotfix2)**

### **Baseline Stability Principle**
**Problem Solved:** Previous logic allowed single-month ticket spikes to cause unwanted promotions from inconsistent → consistent, creating month-to-month classification instability.

**Solution:** Enhanced promotion logic that requires sustained performance over multiple months.

### **Current Implementation (Conservative Approach)**
```python
elif prev_status == 'inconsistent':
    # Enhanced promotion logic: requires sustained performance (3+ consecutive months ≥6 tickets)
    # For now, maintain baseline stability - no promotions until sustained performance tracking is implemented
    chronic_inconsistent.append(circuit_id)
    if rolling_tickets >= CONSISTENT_THRESHOLD:
        circuit_ticket_data[circuit_id]['status'] = 'inconsistent (≥6 tickets this month - monitoring for sustained performance)'
    else:
        circuit_ticket_data[circuit_id]['status'] = 'inconsistent'
```

### **Key Features:**
1. **No Automatic Promotions:** Inconsistent circuits remain inconsistent regardless of current month ticket volume
2. **Performance Monitoring:** Circuits hitting ≥6 tickets are flagged for sustained performance tracking
3. **Baseline Stability:** Maintains consistent 16/12 split in August baseline
4. **Future Ready:** Prepared for full sustained performance tracking implementation

### **Special Status Indicators:**
- `inconsistent (≥6 tickets this month - monitoring for sustained performance)` - High-performing inconsistent circuit
- `consistent (dropped below 6 tickets)` - Consistent circuit with temporary low activity
- `consistent (promoted from inconsistent)` - **No longer used** - prevented by enhanced logic

### **Future Enhancement Path:**
**Phase 2:** Implement full sustained performance tracking:
- **Requirement:** 3+ consecutive months with ≥6 tickets for promotion
- **Analytics Integration:** Track promotion candidates and performance trends
- **Highlighted Promotions:** Flag promoted circuits in reports for operations teams

---

## 📊 **Data Processing Pipeline**

### **1. Deduplication Logic**
**Function:** `_clean_outage()` in `monthly_builder.py`

**Critical Process:**
```python
# Removes duplicate incident counting based on:
# - Config Item Name
# - Distinct count of Inc Nbr
```

**Impact:** Prevents inflated ticket counts that would cause incorrect classifications

**Example:** 118 rows → 101 rows after deduplication (17 duplicates removed)

### **2. Availability Calculation Method** 
**Critical Rule:** Always use `'SUM Outage (Hours)'` column from counts file when available.

**Reference Implementation:** Based on v2.20-rc2-p5b commit analysis
```python
if 'SUM Outage (Hours)' in merged_data.columns:
    # Use pre-calculated hours from counts file (PREFERRED)
    availability = calculate_availability_from_sum_hours()
else:
    # Fallback to converted seconds from impacts file
    availability = calculate_availability_from_seconds()
```

**Accuracy Requirement:** Must match reference calculations within 0.1%

**Historical Fix:** Resolved availability calculation crisis where values were showing impossible negative percentages.

### **3. Circuit Normalization**
**Function:** `get_canonical_id()` in `utils.py`

**Process:**
- Strips vendor prefixes and suffixes  
- Normalizes naming variations
- Prevents duplicate circuit counting under different names
- Maps to authoritative circuit inventory when available

**Common Normalizations:**
```
PCCW SR216187 → SR216187
NTT LZA010663 → LZA010663  
Cirion 500335805 → 500335805
```

### **4. Interface Contamination Prevention**
**Problem:** Network interfaces appearing in circuit lists (e.g., `GigabitEthernet0/0/0/5`)

**Detection Pattern:**
```python
interface_patterns = [
    r'GigabitEthernet\d+/\d+/\d+/\d+',
    r'FastEthernet\d+/\d+',
    r'TenGigabitEthernet\d+/\d+/\d+/\d+'
]
```

**Action:** Interfaces filtered to performance monitoring only, never promoted to chronic status.

**Exception:** `INT-BRW1-LA1-ETH-01` is a legitimate circuit name, not an interface.

---

## 🗃️ **Baseline Management**

### **Current August 2025 Baseline: 28 Circuits**

**Breakdown:**
- **Consistent (16 circuits):** High-activity chronic circuits (≥6 tickets/month)
- **Inconsistent (12 circuits):** Low-activity chronic circuits (<6 tickets/month)
- **Media Chronics (11 circuits):** Separate tracking for media-related circuits
- **Total Chronic:** 28 (excludes media chronics from main count)

**Key Circuits Added in Recent Updates:**
1. `445618042` - Added to inconsistent (4th new chronic from extended analysis)
2. `LZA010635` - Added to inconsistent (strong 7-month candidate)
3. `091NOID1143037092974_993502` - Added to inconsistent (TATA circuit)
4. `KTA SNG EPL 90030013` - Added to inconsistent (Telstra circuit)

### **Historical Data Loading**
**Function:** `load_all_previous_chronics()` in `monthly_builder.py`

**Process:**
1. Scans `history/YYYY-MM/chronic_summary_Month.json` files
2. Extracts all chronic classifications from previous months
3. Merges into master chronic list  
4. Preserves consistent/inconsistent status across months

**Fallback:** If no historical data exists, uses frozen baseline from `docs/frozen_legacy_list.json`

### **New Chronic Identification**
**Progression Path:** Performance Monitoring → Chronic Status

**Stages:**
1. **60-Day Performance Watch:** 2+ incidents in first month
2. **30-Day Performance Watch:** Continued activity in second month  
3. **Chronic Inconsistent:** 3rd consecutive month with activity
4. **Potential Promotion:** After sustained high performance (future enhancement)

**Current Implementation:** Automatically identifies circuits reaching 3-month threshold from performance monitoring progression.

---

## 🔧 **Troubleshooting & Validation**

### **Expected Output Validation**
**August 2025 Baseline:**
```
TOTAL CHRONIC CIRCUITS: 28
CHRONIC CONSISTENT (16 circuits):
CHRONIC INCONSISTENT (12 circuits):
```

**Critical Validation Points:**
- Total count must equal 28
- Consistent + Inconsistent must equal 28  
- No automatic promotions from inconsistent → consistent
- Circuits hitting ≥6 tickets flagged with monitoring status

### **Common Issues & Solutions**

**Issue:** Unwanted promotions causing classification flips
```
❌ Before: inconsistent → consistent (single month spike)
✅ After: inconsistent (≥6 tickets this month - monitoring for sustained performance)
```

**Issue:** Interface contamination in chronic lists
```
❌ Problem: GigabitEthernet0/0/0/5 appearing as chronic
✅ Solution: Filtered to performance monitoring only
```

**Issue:** Duplicate circuit counting
```
❌ Problem: Same circuit counted multiple times with naming variations
✅ Solution: Canonical ID normalization and deduplication
```

**Issue:** Impossible availability percentages  
```
❌ Problem: Negative availability values due to calculation method
✅ Solution: Use 'SUM Outage (Hours)' from counts file
```

### **Testing Methodology**
**Regression Test:** `test_availability_calculation_v2.py`
- Validates availability calculations against reference values
- Ensures accuracy within 0.1% tolerance
- Prevents future calculation regressions

**Integration Testing:**
```bash
# Test with known good data
python monthly_builder.py --impacts "test_impacts.xlsx" --counts "test_counts.xlsx" --month "August"

# Validate expected outputs:
# - 28 total chronic circuits
# - 16 consistent + 12 inconsistent split  
# - No unwanted promotions
# - Proper status flags
```

---

## 💻 **Code Implementation Details**

### **Key Functions & Locations**

**Core Chronic Logic:** `monthly_builder.py` lines 580-650
```python
def process_chronic_circuits():
    # Main function orchestrating chronic identification and classification
    # Loads historical data, processes current month, applies business rules
```

**Enhanced Promotion Logic:** `monthly_builder.py` lines 619-626
```python
elif prev_status == 'inconsistent':
    # Enhanced logic prevents unwanted promotions
    # Maintains baseline stability until sustained performance tracking
```

**Deduplication:** `monthly_builder.py` `_clean_outage()` function
```python
def _clean_outage(df):
    # Removes duplicate incident counting
    # Critical for accurate ticket volume calculations
```

**Historical Loading:** `load_all_previous_chronics()` function
```python  
def load_all_previous_chronics():
    # Scans history folders for previous chronic classifications
    # Implements "once chronic, always chronic" principle
```

### **Configuration Parameters**
```python
CONSISTENT_THRESHOLD = 6  # Tickets required for consistent classification
CHRONIC_MONTHS = 3        # Months required to become chronic
```

**File Structure:**
```
/Users/teffy/Desktop/reporting/
├── monthly_builder.py              # Core logic implementation
├── history/YYYY-MM/                # Historical chronic data
│   ├── chronic_summary_Month.json  # Complete chronic classifications  
│   └── chronic_circuits_list_Month.txt # Human-readable summaries
├── final_output/                   # Current month outputs
└── docs/frozen_legacy_list.json   # Baseline fallback data
```

### **Integration Points**
**Input Processing:**
- `--impacts`: Performance metrics from Tableau
- `--counts`: Chronic identification data from ServiceNow/Tableau
- Historical data loading from previous months

**Output Generation:**
- JSON summaries for system processing
- Word documents for business stakeholders  
- Text files for operations teams
- Charts for executive reporting

---

## 🚀 **Version History & Future Enhancements**

### **v0.1.9-hotfix2 (Current) - Enhanced Promotion Logic**
**Key Achievement:** Eliminated unwanted inconsistent → consistent promotions
- Baseline stability maintained (28 circuits: 16 consistent + 12 inconsistent)
- Performance monitoring flags for high-performing inconsistent circuits
- Foundation laid for sustained performance tracking

### **Future Enhancement: Full Sustained Performance Tracking**
**Planned Implementation:**
- **3+ Consecutive Month Requirement:** Track performance over multiple reporting periods
- **Promotion Analytics:** Comprehensive tracking of promotion candidates
- **Automated Reporting:** Highlight promoted circuits in monthly reports
- **Configuration Management:** Externalize thresholds and criteria

### **Future Enhancement: Real-time Integration**  
**Vision:** Direct ServiceNow API connectivity for live chronic circuit monitoring
- Eliminate manual file exports
- Real-time performance thresholds
- Automated alerting for new chronic circuits

---

## 📞 **Quick Reference**

### **Decision Tree: Is This Circuit Chronic?**
```
1. Has circuit appeared in 3+ consecutive months? 
   → YES: Circuit is chronic
   → NO: Circuit is in performance monitoring

2. If chronic, what classification?
   → ≥6 tickets this month: Consistent (if previously consistent) OR Inconsistent (if previously inconsistent) 
   → <6 tickets this month: Keep previous classification

3. Can inconsistent circuits be promoted?
   → Current logic: NO (prevents classification flips)
   → Future logic: YES (with sustained performance requirement)
```

### **Emergency Reference: Key Numbers**
- **Total Chronic Circuits (August 2025):** 28
- **Consistent:** 16 circuits  
- **Inconsistent:** 12 circuits
- **Chronic Threshold:** 3 consecutive months
- **Consistent Threshold:** 6 tickets per month
- **No Automatic Promotions:** Inconsistent circuits remain inconsistent

### **File Locations for Quick Access**
- **Current Report:** `/final_output/chronic_circuits_list_August.txt`
- **Historical Data:** `/history/2025-08/chronic_summary_August.json`  
- **Core Logic:** `/monthly_builder.py` lines 580-650
- **Test Validation:** `/tests/test_availability_calculation_v2.py`

---

*This document serves as the comprehensive reference for all chronic circuit classification logic. For any questions about business rules, implementation details, or troubleshooting, this is the authoritative source.*