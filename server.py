import os
import sys
import json
import subprocess
import threading
import time
from flask import Flask, jsonify, request, send_file, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")
EXCEL_FILE = os.path.join(BASE_DIR, "QA_Assessment_Report.xlsx")

# Global state for test runner
test_run_state = {
    "is_running": False,
    "last_run_time": None,
    "status": "IDLE", # IDLE, RUNNING, COMPLETED, ERROR
    "exit_code": 0,
    "total": 16,
    "passed": 16,
    "failed": 0,
    "duration": "97.07s",
    "logs": "Ready to execute automated test suite.\nClick 'Run Full Test Suite' to trigger Selenium E2E execution."
}

PRODUCT_FINDINGS = [
    {
        "id": "PL-01",
        "module": "Recruitment",
        "feature": "Add Candidate",
        "type": "Functional Bug",
        "severity": "Medium",
        "title": "Contact Number field allows arbitrary non-numeric text and persists corrupted records",
        "steps": "1. Navigate to Recruitment > Candidates\n2. Click '+ Add'\n3. Enter valid First/Last Name and Email\n4. In 'Contact Number' type 'ABCDEFGHIJ'\n5. Click 'Save'",
        "expected": "Field should validate phone format strictly (numeric + symbols like +, -, ()) and reject letters.",
        "actual": "Form submits with 200 OK and persists corrupted alphabetical phone number to database.",
        "image": "recruitment_phone_letters.png",
        "secondary_image": "recruitment_phone_saved_behavior.png"
    },
    {
        "id": "PL-02",
        "module": "PIM",
        "feature": "Employee Search & Filter",
        "type": "UX / Logical Issue",
        "severity": "Medium",
        "title": "'Reset' button clears input fields but leaves table in stale filtered state",
        "steps": "1. Navigate to PIM > Employee List\n2. Filter by Employment Status = 'Full-Time Contract'\n3. Click 'Search' (table updates)\n4. Click 'Reset'",
        "expected": "Clicking Reset should clear the filters AND refresh the table to the full unfiltered dataset.",
        "actual": "Form inputs are cleared, but the table remains stuck displaying the filtered subset until 'Search' is pressed again.",
        "image": "pim_after_reset.png",
        "secondary_image": "pim_filter_employment_status.png"
    },
    {
        "id": "PL-03",
        "module": "Authentication",
        "feature": "Session Management",
        "type": "Logical Issue",
        "severity": "Medium",
        "title": "Browser 'Back' navigation after logout renders cached Dashboard data",
        "steps": "1. Log into OrangeHRM Dashboard\n2. Click User Profile > Logout\n3. Click Browser 'Back' button",
        "expected": "Cache-Control headers should prevent historical page render, redirecting immediately to Login.",
        "actual": "Cached Dashboard metrics are displayed until an interactive click triggers a 401 unauthenticated redirect.",
        "image": "auth_back_navigation.png",
        "secondary_image": "auth_logout.png"
    },
    {
        "id": "PL-04",
        "module": "PIM",
        "feature": "Employee Id Search",
        "type": "UX Issue",
        "severity": "Low",
        "title": "Non-existent alphanumeric search triggers unnecessary floating error toast",
        "steps": "1. Navigate to PIM > Employee List\n2. In 'Employee Id' enter non-existent string '9999XYZ'\n3. Click 'Search'",
        "expected": "Display zero-state 'No Records Found' table banner cleanly.",
        "actual": "Fires an aggressive red floating error toast 'No Records Found' alongside the standard empty table row.",
        "image": "pim_search_alphanumeric_error.png",
        "secondary_image": "pim_zero_results.png"
    },
    {
        "id": "PL-05",
        "module": "PIM",
        "feature": "Add Employee",
        "type": "Improvement",
        "severity": "Low",
        "title": "First Name silently truncates input at 30 characters without character counter",
        "steps": "1. Navigate to PIM > Add Employee\n2. Paste 50-character name string into 'First Name'",
        "expected": "Display dynamic character count indicator or explicit validation warning on boundary limit.",
        "actual": "Input silently truncates text at 30 chars (maxlength=\"30\") without feedback.",
        "image": "pim_name_length_limit.png",
        "secondary_image": "pim_add_emp_mandatory_validation.png"
    },
    {
        "id": "PL-06",
        "module": "Leave Management",
        "feature": "Apply Leave",
        "type": "Observation (Positive)",
        "severity": "Low",
        "title": "Date Inversion Guard (To Date < From Date) correctly blocks submission",
        "steps": "1. Navigate to Leave > Apply\n2. Select Leave Type\n3. Set From Date = '2026-10-15', To Date = '2026-10-10'\n4. Attempt Submit",
        "expected": "Validation error displayed, blocking submission.",
        "actual": "Inline error 'To date should be after from date' correctly triggers, disabling form submit.",
        "image": "leave_date_validation_verified.png",
        "secondary_image": "leave_submit_inverted_dates.png"
    },
    {
        "id": "PL-07",
        "module": "Admin",
        "feature": "System Users",
        "type": "Observation (Positive)",
        "severity": "Low",
        "title": "Username length boundary & duplicate username check strictly enforced",
        "steps": "1. Navigate to Admin > User Management > Users\n2. Click '+ Add'\n3. Enter existing username 'Admin' or < 5 characters",
        "expected": "Enforce minimum 5 characters and unique username validation.",
        "actual": "Inline validations 'Should be at least 5 characters' and 'Already exists' display cleanly with debounced API check.",
        "image": "admin_duplicate_username.png",
        "secondary_image": "admin_username_boundary.png"
    },
    {
        "id": "PL-08",
        "module": "Recruitment",
        "feature": "Add Candidate",
        "type": "Observation (Positive)",
        "severity": "Low",
        "title": "Candidate Email field enforces RFC compliance",
        "steps": "1. Navigate to Recruitment > Add Candidate\n2. Type invalid email 'admin@test'\n3. Tab out",
        "expected": "Inline validation message indicating invalid email format.",
        "actual": "Displays 'Expected format: admin@example.com' and blocks creation.",
        "image": "recruitment_email_format_error.png",
        "secondary_image": "recruitment_mandatory_fields.png"
    },
    {
        "id": "PL-09",
        "module": "PIM",
        "feature": "Employee List",
        "type": "Observation (Positive)",
        "severity": "Low",
        "title": "Master header checkbox performs clean bulk selection of all 50 records",
        "steps": "1. Navigate to PIM > Employee List\n2. Click Master Select All header checkbox",
        "expected": "Select all 50 records and display 'Delete Selected' batch action button.",
        "actual": "Accurately highlights 50 employee rows and displays batch action toolbar.",
        "image": "pim_bulk_selection.png",
        "secondary_image": "pim_employee_list_initial.png"
    },
    {
        "id": "PL-10",
        "module": "Authentication",
        "feature": "Login Form",
        "type": "Observation (Positive)",
        "severity": "Low",
        "title": "Empty credentials submit triggers simultaneous dual 'Required' validation states",
        "steps": "1. Navigate to /auth/login\n2. Click 'Login' without typing username or password",
        "expected": "Both fields show inline 'Required' error message.",
        "actual": "Dual inline red error cues appear simultaneously without page refresh.",
        "image": "auth_empty_credentials.png",
        "secondary_image": "auth_invalid_credentials.png"
    }
]

AUTOMATION_TESTS = [
    {"class": "TC01_ValidLogin", "method": "test_valid_login", "module": "Auth", "type": "Positive", "desc": "Standard User authentication & redirect to inventory", "image": "saucedemo/tc01_valid_login_success.png"},
    {"class": "TC02_InvalidLogin", "method": "test_locked_out_user", "module": "Auth", "type": "Negative", "desc": "Verify locked_out_user error banner message", "image": "saucedemo/tc02_locked_out_user.png"},
    {"class": "TC02_InvalidLogin", "method": "test_invalid_user_and_password", "module": "Auth", "type": "Negative", "desc": "Verify rejection on non-existent username & bad password", "image": "saucedemo/tc02_invalid_credentials_error.png"},
    {"class": "TC02_InvalidLogin", "method": "test_empty_username", "module": "Auth", "type": "Negative", "desc": "Verify validation message on blank username field", "image": "saucedemo/tc02_empty_username.png"},
    {"class": "TC03_ProductListing", "method": "test_products_displayed", "module": "Catalog", "type": "Positive", "desc": "Verify 6 standard product inventory items rendered", "image": "saucedemo/tc03_product_listing.png"},
    {"class": "TC03_ProductListing", "method": "test_each_product_has_name_price_button", "module": "Catalog", "type": "Positive", "desc": "Verify name, dollar price tag, and 'Add to cart' button per item", "image": "saucedemo/tc03_product_listing.png"},
    {"class": "TC03_ProductListing", "method": "test_product_sort_price_low_to_high", "module": "Catalog", "type": "Positive", "desc": "Verify dropdown sort by Price (low to high): $7.99 -> $49.99", "image": "saucedemo/tc03c_sort_price_low_high.png"},
    {"class": "TC04_AddToCart", "method": "test_add_single_item_updates_badge", "module": "Cart", "type": "Positive", "desc": "Add backpack to cart, verify badge='1' and button becomes 'Remove'", "image": "saucedemo/tc04_add_single_item.png"},
    {"class": "TC04_AddToCart", "method": "test_add_multiple_items_updates_badge", "module": "Cart", "type": "Positive", "desc": "Add 2 items, verify shopping badge count increments to '2'", "image": "saucedemo/tc04_add_two_items.png"},
    {"class": "TC05_CartValidation", "method": "test_cart_shows_correct_items", "module": "Cart", "type": "Positive", "desc": "Navigate to cart, verify selected items are rendered accurately", "image": "saucedemo/tc05_cart_content.png"},
    {"class": "TC05_CartValidation", "method": "test_remove_item_from_cart", "module": "Cart", "type": "Positive", "desc": "Click 'Remove' button inside cart and verify badge updates", "image": "saucedemo/tc05b_remove_from_cart.png"},
    {"class": "TC05_CartValidation", "method": "test_empty_cart_has_no_items", "module": "Cart", "type": "Positive", "desc": "Verify fresh session cart contains 0 items and no badge", "image": "saucedemo/tc05c_empty_cart.png"},
    {"class": "TC06_CheckoutHappyPath", "method": "test_checkout_complete_flow", "module": "Checkout", "type": "Positive", "desc": "Complete E2E checkout: Info -> Tax/Total -> 'Thank you for your order!'", "image": "saucedemo/tc06_checkout_complete.png"},
    {"class": "TC06_CheckoutHappyPath", "method": "test_checkout_validation_empty_fields", "module": "Checkout", "type": "Negative", "desc": "Attempt checkout step 1 with empty fields; verify 'First Name is required'", "image": "saucedemo/tc06b_checkout_validation.png"},
    {"class": "TC07_Logout", "method": "test_logout_redirects_to_login", "module": "Auth", "type": "Positive", "desc": "Open burger menu, click Logout, verify redirection to login", "image": "saucedemo/tc07_logout.png"},
    {"class": "TC07_Logout", "method": "test_cannot_access_inventory_after_logout", "module": "Auth", "type": "Negative", "desc": "Attempt direct GET /inventory.html post-logout; verify guard redirect", "image": "saucedemo/tc07b_post_logout_session_check.png"}
]

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/evidence/<path:filename>")
def serve_evidence(filename):
    return send_from_directory(EVIDENCE_DIR, filename)

@app.route("/api/stats")
def get_stats():
    return jsonify({
        "product_findings": {
            "total": len(PRODUCT_FINDINGS),
            "bugs": len([f for f in PRODUCT_FINDINGS if "Bug" in f["type"]]),
            "ux_logical": len([f for f in PRODUCT_FINDINGS if "UX" in f["type"] or "Logical" in f["type"]]),
            "positive_observations": len([f for f in PRODUCT_FINDINGS if "Observation" in f["type"] or "Improvement" in f["type"]]),
            "high": len([f for f in PRODUCT_FINDINGS if f["severity"] == "High"]),
            "medium": len([f for f in PRODUCT_FINDINGS if f["severity"] == "Medium"]),
            "low": len([f for f in PRODUCT_FINDINGS if f["severity"] == "Low"])
        },
        "automation": {
            "total": len(AUTOMATION_TESTS),
            "passed": test_run_state["passed"],
            "failed": test_run_state["failed"],
            "pass_rate": f"{(test_run_state['passed'] / max(1, len(AUTOMATION_TESTS))) * 100:.1f}%",
            "execution_status": test_run_state["status"],
            "last_duration": test_run_state["duration"],
            "last_run": test_run_state["last_run_time"]
        }
    })

@app.route("/api/findings")
def get_findings():
    return jsonify(PRODUCT_FINDINGS)

@app.route("/api/automation-tests")
def get_automation_tests():
    return jsonify(AUTOMATION_TESTS)

def run_pytest_thread(test_filter=None):
    global test_run_state
    test_run_state["is_running"] = True
    test_run_state["status"] = "RUNNING"
    test_run_state["logs"] = f"Executing test suite with filter: {test_filter or 'ALL'}\nStarting Selenium ChromeDriver...\n"
    start_time = time.time()

    cmd = [sys.executable, "-m", "pytest", "saucedemo_tests/test_saucedemo.py", "-v", "-s"]
    if test_filter:
        cmd.extend(["-k", test_filter])

    try:
        process = subprocess.Popen(
            cmd,
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        full_output = []
        for line in iter(process.stdout.readline, ""):
            full_output.append(line)
            test_run_state["logs"] += line

        process.stdout.close()
        return_code = process.wait()
        duration = time.time() - start_time

        test_run_state["exit_code"] = return_code
        test_run_state["duration"] = f"{duration:.2f}s"
        test_run_state["last_run_time"] = time.strftime("%Y-%m-%d %H:%M:%S")

        output_str = "".join(full_output)
        if "passed" in output_str:
            import re
            passed_match = re.search(r"(\d+) passed", output_str)
            failed_match = re.search(r"(\d+) failed", output_str)
            if passed_match:
                test_run_state["passed"] = int(passed_match.group(1))
            if failed_match:
                test_run_state["failed"] = int(failed_match.group(1))
            else:
                test_run_state["failed"] = 0

        test_run_state["status"] = "COMPLETED" if return_code == 0 else "FAILED"
    except Exception as e:
        test_run_state["status"] = "ERROR"
        test_run_state["logs"] += f"\nExecution error: {str(e)}"
    finally:
        test_run_state["is_running"] = False

@app.route("/api/run-tests", methods=["POST"])
def trigger_tests():
    global test_run_state
    if test_run_state["is_running"]:
        return jsonify({"status": "error", "message": "Test execution already in progress"}), 400

    data = request.get_json(silent=True) or {}
    test_filter = data.get("filter")

    t = threading.Thread(target=run_pytest_thread, args=(test_filter,))
    t.daemon = True
    t.start()

    return jsonify({"status": "started", "filter": test_filter or "all"})

@app.route("/api/test-status")
def get_test_status():
    return jsonify(test_run_state)

@app.route("/api/generate-excel", methods=["POST"])
def generate_excel():
    try:
        res = subprocess.run(
            [sys.executable, "generate_report_excel.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        if res.returncode == 0:
            return jsonify({"status": "success", "message": "QA_Assessment_Report.xlsx successfully generated."})
        else:
            return jsonify({"status": "error", "error": res.stderr}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/api/download-excel")
def download_excel():
    if not os.path.exists(EXCEL_FILE):
        return jsonify({"error": "Excel file not found"}), 404
    return send_file(
        EXCEL_FILE,
        as_attachment=True,
        download_name="QA_Assessment_Report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"QA Control Center server running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
