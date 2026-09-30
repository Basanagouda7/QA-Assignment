# QA Assessment Control Center & Automation Suite

Comprehensive QA practical assessment covering **Product-Level Testing (OrangeHRM SaaS)** and an **Automated E2E Test Suite (SauceDemo)** with Selenium WebDriver, Python, and a **Full-Stack QA Web Dashboard**.

---

## 🌟 Interactive QA Control Center (UI + Backend)

A modern full-stack web application integrating real-time test execution, live console streaming, product findings matrix, screenshot evidence gallery, and automated report exporter.

### Features
- **Live Test Runner Console**: Trigger full test suites or individual isolated tests with real-time streaming terminal logs.
- **Executive Metrics & Analytics**: Pass rate rings, execution duration, and severity distribution.
- **Product QA Matrix (OrangeHRM)**: Searchable, filterable 10 verified findings with reproduction steps and screenshot zoom.
- **Evidence Lightbox Gallery**: Instant zoom and inspection of exploratory and test captures.
- **One-Click Deliverable Exporter**: Rebuild and download [`QA_Assessment_Report.xlsx`](QA_Assessment_Report.xlsx) on demand.

### Launching the Web Application
```powershell
python server.py
```
Open your browser at: **`http://localhost:5000`**

---

## 📋 Assessment Deliverables

1. **Interactive Control Center**: Launch with `python server.py` (visit `http://localhost:5000`)
2. **Executive QA Report**: [`QA_EXECUTION_REPORT.md`](QA_EXECUTION_REPORT.md)
3. **Standardized Assessment Matrix**: [`QA_Assessment_Report.xlsx`](QA_Assessment_Report.xlsx) (Formatted Excel spreadsheet containing Sheet 1: *Product-Level Testing* & Sheet 2: *Automation Testing*)
4. **Automated E2E Test Suite**: [`saucedemo_tests/test_saucedemo.py`](saucedemo_tests/test_saucedemo.py)
5. **Visual Evidence & Screenshots**: [`evidence/`](evidence/)

---

## 🚀 CLI Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Automated Tests via Pytest
```bash
# Run complete test suite (16 tests)
python -m pytest saucedemo_tests/test_saucedemo.py -v -s

# Run single test in isolation
python -m pytest saucedemo_tests/test_saucedemo.py -k "test_valid_login" -v -s
```

### 3. Rebuild Excel Assessment Matrix
```bash
python generate_report_excel.py
```
