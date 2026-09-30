# QA Assignment & Automation Suite

Comprehensive QA practical assessment covering **Product-Level Testing (OrangeHRM SaaS)** and **Automated E2E Test Suite (SauceDemo)** with Selenium WebDriver & Python.

---

## 📋 Deliverables Overview

1. **Executive QA Report**: [`QA_EXECUTION_REPORT.md`](QA_EXECUTION_REPORT.md)
2. **Standardized Assessment Matrix**: [`QA_Assessment_Report.xlsx`](QA_Assessment_Report.xlsx) (Formatted Excel spreadsheet containing Sheet 1: *Product-Level Testing* & Sheet 2: *Automation Testing*)
3. **Automated Test Suite**: [`saucedemo_tests/test_saucedemo.py`](saucedemo_tests/test_saucedemo.py)
4. **Visual Evidence & Screenshots**: [`evidence/`](evidence/)

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Google Chrome browser

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
pytest saucedemo_tests/test_saucedemo.py -v -s
```

### 4. Regenerate Excel Assessment Matrix (Optional)
```bash
python generate_report_excel.py
```
