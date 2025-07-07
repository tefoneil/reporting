# Hybrid Consistency Mode – Operational Spec  
*(approved 2025-07-07)*

---

## 1 Purpose
Blend the legacy, manually-curated Consistent / Inconsistent list with the new
ticket-based rule **without disrupting leadership's familiar view**.

*   All circuits chronic **through May 2025** keep their existing status.
*   Any circuit that becomes chronic **after** May 2025 is classified by
    rolling ticket volume (≥ 6 tickets over the 3-month window ⇒ Consistent).

---

## 2 Key Parameters

| Item | Value |
|------|-------|
| **Cut-over month** | **May 2025** |
| **Ticket threshold** | `CONSISTENT_THRESHOLD = 6` |
| **Mode label** | `"consistency_mode": "hybrid"` (JSON) & one-line footer in Word doc |

---

## 3 Classification Logic

```python
if cid in baseline_legacy_status:              # chronic up to 2025-05
    status = baseline_legacy_status[cid]       # freeze legacy value
elif months_chronic >= 3 and cid not in baseline_ids:
    status = "New Chronic"                     # first month hitting chronic
else:
    status = (
        "Consistent" if rolling_tickets[cid] >= CONSISTENT_THRESHOLD
        else "Inconsistent"
    )
```

* `baseline_legacy_status` is read from **chronic\_summary\_2025-05.json**
  (or earliest prior summary present).

---

## 4 JSON Output Changes

```json
{
  "version": "0.1.4",
  "consistency_mode": "hybrid",
  "rolling_ticket_total": 9,
  "status": "Consistent"
}
```

*Legacy status is still stored for circuits frozen before the cut-over.*

---

## 5 GUI / CLI Behaviour

* **No new fields** – workflow unchanged.
* If the collector finds **no prior summaries**, the banner:

```
⚠️  No prior summaries found – all chronic circuits will repeat as
'New Chronic' this run.
```

remains in place.

---

## 6 Testing Requirements

| Test                                                  | Expectation                                                          |
| ----------------------------------------------------- | -------------------------------------------------------------------- |
| **Legacy circuit** (in 2025-05 JSON)                  | Status unchanged after run.                                          |
| **Dummy circuit 7 tickets** (new chronic + 7 tickets) | Promoted to **Consistent** next month.                               |
| **Dummy circuit 4 tickets** (new chronic + 4 tickets) | Promoted to **Inconsistent** next month.                             |
| **Env threshold override**                            | `MR_CONSISTENT_THRESHOLD=8` makes test circuits require ≥ 8 tickets. |

---

## 7 CHANGELOG Entry

```markdown
## [0.1.4] – 2025-07-07
### Added
- **Hybrid consistency mode**  
  - Legacy Consistent/Inconsistent statuses frozen up to May 2025.  
  - All new chronic circuits use rolling ticket rule (≥ 6 tickets) for status.
- JSON fields: `"version": "0.1.4"`, `"consistency_mode"`.
### Fixed
- Warning banner now fires when no prior summaries are found.
```

---

## 8 Deployment Steps

1. Claude implements code & unit tests per this spec.
2. Merge → run smoke/integration tests.
3. Tag **v0.1.4**.
4. Re-run **June 2025** report:

   * Total circuits should increase to at least **24**.
   * `444282783` moves from *New Chronic* to Consistent/ Inconsistent based on tickets.

---

*Document owner: PMA • Revision 1*