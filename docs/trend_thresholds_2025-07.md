# Threshold Policy – Core vs. Monthly Trend Analysis  
*(approved 2025-07-08)*

---

## 1  Core Chronic Classification  (unchanged)

| Metric | Threshold |
|--------|-----------|
| Tickets (Consistent rule) | `CONSISTENT_THRESHOLD = 6` |
| Cost change used in chronic tables | ≥ **$1 000** |
| Availability swing | ≥ **5 pp** |
| MTBF swing | ≥ **0.5 days** |
| Rank change (Top/Bottom-5 lists) | ≥ **2 positions** |

These constants drive the **chronic counts, Consistent/Inconsistent
status, performance monitoring, graphs, and Word-doc tables**.  
They do **not** change in v0.1.7-b.

---

## 2  Monthly Trend Analysis (these are the *only* thresholds lowered)

```python
TREND_THRESH = {
    "tickets": 1,        # was 3
    "cost_usd": 500,     # was 1 000
    "availability_pct": 2,  # was 5
    "mtbf_days": 0.2,    # was 0.5
    "rank": 1,           # was 2
}
```

* Applied **only** inside `generate_monthly_trend_analysis()`.
* Core chronic numbers are completely unaffected.
* Hidden behind ENV overrides if future tuning is needed:

```bash
export MR_TREND_TICKETS=2
export MR_TREND_AVAIL_PCT=3
```

---

## 3  Safeguards

* If **previous-month JSON** is missing the Trend section logs a
  yellow banner:

  ```
  ⚠️  Trend Analysis skipped – prior summary not found in folder.
  ```

* Data-quality banner remains for > 10 % non-numeric ticket cells.

---

## 4  CHANGELOG excerpt

```markdown
## [0.1.7-b] – 2025-07-08
### Changed
- Lowered thresholds **only** for *Monthly Trend Analysis*  
  (tickets ≥1, cost ≥$500, availability ≥2 pp, MTBF ≥0.2 days, rank ≥1).
- Core chronic classification thresholds remain unchanged.
- Added warning when prior-month summary JSON is missing.
```

---

*Document owner: PMA • Revision 2*