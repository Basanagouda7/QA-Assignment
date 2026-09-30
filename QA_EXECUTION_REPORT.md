# QA Engineering Practical Screening Assessment Report

**Role Focus**: Senior QA Engineer / Product Tester  
**Date**: September 2026  
**Deliverable Artifact**: [`QA_Assessment_Report.xlsx`](QA_Assessment_Report.xlsx) (Contains Sheet 1: *Product-Level Testing* & Sheet 2: *Automation Testing*)

---

## Executive Summary

This comprehensive practical testing assessment evaluates end-to-end product thinking, manual exploratory testing, logical/business defect identification, and robust Selenium WebDriver automation.

### Key Metrics
- **OrangeHRM Product-Level Findings Documented**: 10 distinct, evidence-backed items
  - **Functional Bugs / Logical Issues**: 3 (Recruitment Phone Validation, PIM Reset UX, Post-Logout Back Navigation)
  - **UX / Improvements**: 2 (PIM Search Zero-State Toast, Name Field Length Boundary)
  - **Verified Positive Behaviors**: 5 (Date Inversion Logic, Username Duplicate/Boundary Rules, Email RFC Validator, PIM Bulk Selection, Required Field Enforcement)
- **Severity Distribution**:
  - High: 0 (No critical server crash/data-wiping defects found in tested scope)
  - Medium: 3 (Data corruption in candidate contact, decoupled search reset UX, cached session history)
  - Low: 7 (Usability, input feedback, and positive validation baselines)
- **SauceDemo Automation Suite**:
  - **Total Scenarios Automated**: 16 test methods across 7 core test classes
  - **Execution Pass Rate**: 100% (16 Passed, 0 Failed, 0 Errors)
  - **Execution Time**: ~98s (headless Chrome)

---

## Part 1: Product-Level Testing (OrangeHRM SaaS)

**Target URL**: `https://opensource-demo.orangehrmlive.com/`  
**Role Persona Tested**: HR Administrator, Talent Recruiter, Operations Manager

### Verified Issues & Observations Table Summary

| ID | Module / Page | Feature / Flow | Issue Type | Severity | Key Finding |
|---|---|---|---|---|---|
| **PL-01** | Recruitment | Add Candidate | Functional Bug | **Medium** | Contact Number field accepts alphabetical/arbitrary strings and persists corrupted candidate records to database. |
| **PL-02** | PIM | Employee Search & Filter | UX Issue | **Medium** | "Reset" button clears input fields but leaves the table in an outdated filtered state until manually re-queried. |
| **PL-03** | Authentication | Session Management | Logical Issue | **Medium** | Browser "Back" button after logout renders cached Dashboard metrics on shared workstations. |
| **PL-04** | PIM | Employee Id Search | UX Issue | **Low** | Non-existent alphanumeric search triggers an unnecessary floating error toast alongside the zero-state table message. |
| **PL-05** | PIM | Add Employee | Improvement | **Low** | First Name silently truncates text at 30 characters (`maxlength="30"`) without a counter or visual cue. |
| **PL-06** | Leave Management | Apply Leave | Observation | **Low** | Date inversion (To Date < From Date) correctly displays inline validation and blocks form submission. |
| **PL-07** | Admin | System Users | Observation | **Low** | Username validation strictly enforces >=5 characters and debounced duplicate detection (`Admin`). |
| **PL-08** | Recruitment | Add Candidate | Observation | **Low** | Candidate email input strictly enforces RFC format (`Expected format: admin@example.com`). |
| **PL-09** | PIM | Employee List | Observation | **Low** | Master header checkbox accurately selects all 50 rendered cards and exposes "Delete Selected" batch action. |
| **PL-10** | Authentication | Login Form | Observation | **Low** | Submitting empty login credentials triggers simultaneous dual-field inline "Required" error states. |

---

## Part 2: Automation Testing (SauceDemo E-Commerce)

**Target URL**: `https://www.saucedemo.com/`  
**Test Suite Path**: [`saucedemo_tests/test_saucedemo.py`](saucedemo_tests/test_saucedemo.py)  
**Drivers**: Standalone ChromeDriver 114+ with headless execution

### Automated Test Matrix & Execution Status

| Test ID | Test Name | Flow | Type | Status | Regression Risk & Business Impact |
|---|---|---|---|---|---|
| **TC01** | `test_valid_login` | Authentication | Smoke | **PASS** | Critical login route guard; failure halts all downstream purchases. |
| **TC02** | `test_invalid_user_and_password` | Auth Security | Functional | **PASS** | Prevents unauthorized entry and credential enumeration. |
| **TC02b** | `test_locked_out_user` | Account State | Functional | **PASS** | Ensures locked/suspended accounts cannot browse or purchase. |
| **TC02c** | `test_empty_username` | Form Validation | Functional | **PASS** | Validates baseline required field feedback. |
| **TC03** | `test_products_displayed` | Product Catalog | Functional | **PASS** | Verifies 6 catalog items render on inventory load. |
| **TC03b** | `test_each_product_has_name_price_button` | Card Integrity | Functional | **PASS** | Ensures price formatting (`$`) and Add to Cart buttons are present. |
| **TC03c** | `test_product_sort_price_low_to_high` | Catalog Sorting | Regression | **PASS** | Verifies numerical price sorting ascending `[7.99 ... 49.99]`. |
| **TC04** | `test_add_single_item_updates_badge` | Cart State | Functional | **PASS** | Verifies badge updates to '1' and button flips to 'Remove'. |
| **TC04b** | `test_add_multiple_items_updates_badge` | Multi-item Cart | Functional | **PASS** | Verifies cumulative cart badge incrementing to '2'. |
| **TC05** | `test_cart_shows_correct_items` | Cart Review | Functional | **PASS** | Validates exact product names match selected inventory items. |
| **TC05b** | `test_remove_item_from_cart` | Cart Modification | Functional | **PASS** | Verifies item deletion from cart table and badge removal. |
| **TC05c** | `test_empty_cart_has_no_items` | Cart Zero-State | Functional | **PASS** | Ensures pristine cart state on fresh sessions. |
| **TC06** | `test_checkout_complete_flow` | Checkout Funnel | Smoke | **PASS** | End-to-end checkout with subtotal ($39.98) + tax ($3.20) = $43.18. |
| **TC06b** | `test_checkout_validation_empty_fields` | Checkout Validation | Functional | **PASS** | Validates mandatory First Name requirement on step 1. |
| **TC07** | `test_logout_redirects_to_login` | Session Lifecycle | Smoke | **PASS** | Verifies sidebar burger menu logout flow. |
| **TC07b** | `test_cannot_access_inventory_after_logout` | Route Protection | Regression | **PASS** | Ensures unauthenticated direct URL access redirects to login. |

---

## How to Execute the Automation Suite

### Prerequisites
1. Python 3.10+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Execution Commands
- Run SauceDemo Test Suite:
  ```bash
  python saucedemo_tests/test_saucedemo.py
  ```
- Run Exploratory Auth Tests:
  ```bash
  python exploratory/test_auth.py
  ```
- Run DOM Inspection Utility:
  ```bash
  python exploratory/inspect_dom.py
  ```
- Regenerate Excel Report:
  ```bash
  python generate_report_excel.py
  ```
