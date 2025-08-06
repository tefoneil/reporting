# Complete List of Additional Chronic Circuit Candidates

## Summary
**Total Additional Candidates Beyond Current August Baseline: 27 circuits**

*Note: Current August baseline has 24 circuits (16 consistent + 8 inconsistent)*

---

## VERY STRONG CANDIDATES (7 months persistent) - 5 circuits

**Risk Level: LOW** - Strong historical evidence for addition

1. **091NOID1143035717849**
   - Vendor: TATA
   - Historical persistence: 7 months since January 2025
   - Notes: Long-term chronic, high confidence

2. **091NOID1143037092974_993502** 
   - Vendor: TATA
   - Historical persistence: 7 months since January 2025
   - Notes: Long-term chronic, high confidence

3. **500334193 / 81-4W3EOZV**
   - Vendor: Cirion  
   - Historical persistence: 7 months since January 2025
   - Notes: May be naming variation of existing circuit, needs manual review

4. **A0DV2-A0DV3 NP1 // 091NOID1143035717419_889599**
   - Vendor: TATA
   - Historical persistence: 7 months since January 2025
   - Notes: Complex name, may be variation of existing circuit, needs manual review

5. **LZA010635**
   - Vendor: Liquid Telecom (NTT)
   - Historical persistence: 7 months since January 2025
   - Notes: Strong candidate, same vendor family as existing LZA010663

---

## STRONG CANDIDATES (5-6 months persistent) - 7 circuits

**Risk Level: MEDIUM** - Good historical evidence

### 6 Months Persistent (1 circuit):
1. **KTA SNG EPL 90030013**
   - Vendor: Telstra
   - Historical persistence: 6 months
   - Notes: Same vendor as existing PTH TOK EPL circuits

### 5 Months Persistent (6 circuits):
2. **091NOID1143035717419_1040578**
   - Vendor: TATA
   - Historical persistence: 5 months
   - Notes: Similar naming to existing TATA circuits

3. **443845436**
   - Vendor: Lumen  
   - Historical persistence: 5 months
   - Notes: Lumen vendor circuit

4. **443832799**
   - Vendor: Lumen
   - Historical persistence: 5 months  
   - Notes: Lumen vendor circuit

5. **444282783**
   - Vendor: Lumen
   - Historical persistence: 5 months
   - Notes: Previously identified as new chronic in June reports

6. **LD017936 / FRANFRT/PISAT1-SINGAPOR/PISAT1 10GE1**
   - Vendor: Orange
   - Historical persistence: 5 months
   - Notes: Long descriptive name, appears legitimate circuit

7. **LZA010634**  
   - Vendor: Liquid Telecom (NTT)
   - Historical persistence: 5 months
   - Notes: Same vendor family as existing LZA circuits

---

## MODERATE CANDIDATES (4 months persistent) - 3 circuits

**Risk Level: MEDIUM-HIGH** - Developing pattern

1. **027ISAN284012272923**
   - Vendor: TATA
   - Historical persistence: 4 months
   - Notes: TATA circuit with numeric naming pattern

2. **027ISAN284012326783**
   - Vendor: TATA  
   - Historical persistence: 4 months
   - Notes: Similar TATA circuit family

3. **445252110**
   - Vendor: Lumen
   - Historical persistence: 4 months
   - Notes: Lumen circuit, developing chronic pattern

---

## NEW CHRONIC CANDIDATES (3 months - threshold) - 12 circuits  

**Risk Level: HIGH** - Just reached chronic threshold, monitor for stability

1. **081-56A1UCX - 500365017**
   - Vendor: Cirion
   - Historical persistence: 3 months (new chronic)

2. **088896000016**
   - Vendor: TATA
   - Historical persistence: 3 months (new chronic)

3. **AUT/XBG/LE-293046**  
   - Vendor: Orange
   - Historical persistence: 3 months (new chronic)

4. **443966752**
   - Vendor: Lumen
   - Historical persistence: 3 months (new chronic)

5. **444340547**
   - Vendor: Lumen  
   - Historical persistence: 3 months (new chronic)

6. **444340550**
   - Vendor: Lumen
   - Historical persistence: 3 months (new chronic)

7. **444353160**
   - Vendor: Lumen
   - Historical persistence: 3 months (new chronic)

8. **445498014**
   - Vendor: Lumen
   - Historical persistence: 3 months (new chronic)

9. **445620927**
   - Vendor: Lumen
   - Historical persistence: 3 months (new chronic)

10. **500394765 / 81-5IPQVEY**
    - Vendor: Cirion
    - Historical persistence: 3 months (new chronic)

11. **500394949 / 81-5IPQVEO** 
    - Vendor: Cirion
    - Historical persistence: 3 months (new chronic)

12. **W1E39404**
    - Vendor: Verizon
    - Historical persistence: 3 months (new chronic)

---

## Vendor Distribution of Additional Candidates

- **Lumen**: 10 circuits (37% of additional candidates)
- **TATA**: 6 circuits (22% of additional candidates)  
- **Cirion**: 4 circuits (15% of additional candidates)
- **Liquid Telecom (NTT)**: 2 circuits (7% of additional candidates)
- **Orange**: 2 circuits (7% of additional candidates)
- **Telstra**: 1 circuit (4% of additional candidates)
- **Verizon**: 1 circuit (4% of additional candidates)

## Manual Review Required

### Potential Duplicate Circuit Names:
1. **500334193 / 81-4W3EOZV** vs existing **500334193** - Verify if same circuit  
2. **A0DV2-A0DV3 NP1 // 091NOID1143035717419_889599** vs existing **091NOID1143035717419_889599** - Verify if same circuit
3. **091NOID1143035717849** vs existing **091NOID1143035717849_889621** - Verify if same circuit

### Recommendation:
Before adding any circuits to the chronic list, manually verify these potential duplicates to avoid double-counting the same circuit with different naming conventions.

---

## Technical Issues Correction

**Interface Name Issue**: Only 1 true interface contamination found:
- ❌ `GigabitEthernet0/0/0/5` (legitimate interface - should be removed from performance monitoring)
- ✅ `INT-BRW1-LA1-ETH-01` (legitimate circuit name - user confirmed)  
- ✅ `TPZ-FOC-FRK-ETH-23022` (legitimate circuit name)

---

## Strategic Implementation Recommendations

### Phase 1 (September): Low Risk Additions
- Consider adding 2-3 of the **7-month persistent circuits** after manual duplicate review
- Focus on circuits with clear naming (avoid potential duplicates initially)

### Phase 2 (October): Moderate Risk Additions  
- Add remaining 7-month persistent circuits after duplicate resolution
- Consider strongest 5-6 month persistent circuits

### Phase 3 (November+): New Chronic Monitoring
- Monitor 3-month circuits for continued persistence  
- Add stable 4+ month circuits based on continued evidence

*This gradual approach ensures leadership confidence while expanding chronic identification based on strong historical evidence.*