# Canonical ID Normalization – v0.1.5 Specification

*(approved 2025-07-07)*

---

## Purpose

Eliminate circuit ID variation splitting by normalizing all circuit identifiers to their canonical form before grouping, ticket totals, and chronic status calculations.

---

## Canonical ID Extraction Rules

### Delimiter Precedence

Split on **first** delimiter in this order:

1. `_` (underscore)
2. `/` (forward slash) 
3. ` ` (space)
4. `-` (hyphen) - **only if it follows ≥3 digits**

### Examples

| Raw ID example                           | `canonical_id` |
|------------------------------------------|----------------|
| 091NOID1143035717419_889599              | 091NOID1143035717419 |
| 091NOID1143035717849_889621              | 091NOID1143035717849 |
| SR216187                                 | SR216187 |
| 500335805-CH1                            | 500335805 |
| 500335805-CH1/EXTRA                      | 500335805 |
| LD017936 / FRANFRT-SINGAPOR/PISTA/10GE1  | LD017936 |
| VID-1583                                 | VID-1583 |
| VID-1597                                 | VID-1597 |

### Special Cases

- **VID-1583**: No split (letters before hyphen, not ≥3 digits)
- **Media chronics**: Follow same canonical rule, no special case needed
- **Empty/null values**: Return empty string

---

## Implementation Details

### Data Processing

1. **Forward-fill** the *Month / Year* column **before** any filtering
2. Apply `canonical_id()` to both Crosstab and Counts DataFrames
3. Add `canonical_id` column to enable grouping
4. Sum **`Distinct count of Inc Nbr`** grouped by `canonical_id`

### Baseline Compatibility

- Convert **every baseline ID to canonical form at load-time**
- Use canonical form for all status lookups and comparisons
- Legacy status mapping preserved seamlessly

### Ticket Count Source

- **File**: Count Months Chronic
- **Column**: `Distinct count of Inc Nbr`
- **Method**: Sum by `canonical_id`, ignore Crosstab ticket columns

---

## Data Quality Safeguards

1. **Forward-fill warning**: GUI banner if >10% of month cells were blank
2. **Ticket coercion warning**: GUI banner if >10% of ticket values cannot convert to numeric
3. **Baseline warning**: GUI banner if no prior summaries found

---

## Expected Impact

### Problem Solved
- **091NOID1143035717419_889599** and **091NOID1143035717849_889621** now aggregate as **091NOID1143035717419** and **091NOID1143035717849**
- No more zero-ticket misclassification due to ID variations
- Single source of truth for ticket counts

### Backward Compatibility
- Legacy circuits maintain frozen status from May 2025 baseline
- Original circuit IDs preserved in output for display
- All existing workflows unchanged

---

## Testing Requirements

| Test Case | Expected Result |
|-----------|----------------|
| 091NOID variants with tickets 2+3+1 | One canonical ID with rolling_ticket_total = 6 |
| VID-1583 with hyphen | No split, stays VID-1583 |
| Legacy circuit from baseline | Status frozen regardless of new ticket count |
| New circuit with 7 tickets | Classified as Consistent |
| New circuit with 4 tickets | Classified as Inconsistent |

---

*Document owner: PMA • v0.1.5 specification*