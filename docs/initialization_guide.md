# Monthly Reporting – Initialization Guide v0.1.0
*(Last updated 2025-07-06)*

---

## 1 Purpose

Spin the **Monthly Reporting** module out of the main **ops-toolkit** into its own
private repo — complete with the familiar **FreeSimpleGUI** window, a smoke-test
harness, and zero redaction baggage.  
**Day-to-day users (you and your teammate) will interact solely through the GUI.**

---

## 2 Project Structure

```
reporting/
├── monthly_builder.py          # core engine + FreeSimpleGUI window
├── analyze_data.py             # data-prep utility
├── monthly_reporting_cli.py    # test harness (not for everyday use)
├── __init__.py
├── requirements.txt            # deps incl. FreeSimpleGUI
├── .gitignore
├── tests/
│   ├── sample_impacts.xlsx
│   ├── sample_counts.xlsx
│   ├── smoke_test.sh
│   └── create_sample_data.py
└── docs/
    └── architecture.md
```

### Highlights

| Feature                | Status | Notes                                   |
|------------------------|--------|-----------------------------------------|
| GUI (FreeSimpleGUI)    | **Primary** | The workflow you'll use every month. |
| CLI test harness       | Internal | Powers `tests/smoke_test.sh`; ignore for regular work. |
| Mapping file           | N/A    | Not required. README line removed.      |
| Redaction code         | Gone   | All scrub/mask logic stripped.          |

---

## 3 Dependencies

```text
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
seaborn>=0.11.0
python-docx>=0.8.11
FreeSimpleGUI>=5.0.0
openpyxl>=3.0.0
tqdm>=4.65.0           # progress bars inside the test harness
```

Install:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 4 Running the Tool (GUI workflow)

```bash
python monthly_builder.py
```

1. **Browse** for **Impacts Crosstab.xlsx** and **Count Months Chronic.xlsx**.
2. **Toggle** *Exclude Regional* and *Show Indicators* as needed.
3. **Select** the target month/year.
4. **Generate Report** → Word doc, PNG charts & JSON appear in your chosen folder.

*(The CLI wrapper exists only so automated tests can run; you can ignore it.)*

---

## 5 Smoke Test (dev housekeeping)

```bash
./tests/smoke_test.sh
```

Confirms the codebase still builds a report with synthetic data.
Useful after dependency upgrades or refactors; not part of the monthly routine.

---

## 6 Release Checklist (v0.1.0)

1. Confirm the `Path(...).lower()` bug is fixed (cast to `str()` — done).
2. `./tests/smoke_test.sh` passes.
3. Commit README change removing `mapping.csv`.
4. Tag & push:

```bash
git tag v0.1.0 -m "First standalone release (GUI-only workflow)"
git push origin v0.1.0
```

---

### Roadmap (optional)

* **CI:** smoke test in GitHub Actions.
* **Packaging:** `pyproject.toml` + hatch for internal wheel.
* **Installer:** PyInstaller EXE if broader org adoption happens.
* **New outputs:** JSON → Power BI template if leadership asks.

---

Happy reporting! 🎉