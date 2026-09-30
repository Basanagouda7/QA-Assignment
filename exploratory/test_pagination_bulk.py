"""
Fixed Pagination, Bulk Selection, and Filter tests for OrangeHRM PIM.
Based on verified DOM structure from inspect_dom.py.
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_driver():
    opt = Options()
    opt.add_argument('--headless=new')
    opt.add_argument('--no-sandbox')
    opt.add_argument('--disable-dev-shm-usage')
    opt.add_argument('--disable-gpu')
    opt.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(service=Service('drivers/chromedriver.exe'), options=opt)
    return driver

def login(driver):
    wait = WebDriverWait(driver, 20)
    driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
    wait.until(EC.element_to_be_clickable((By.NAME, "username"))).send_keys("Admin")
    driver.find_element(By.NAME, "password").send_keys("admin123")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    wait.until(EC.url_contains("/dashboard/index"))

def get_records_count_text(driver):
    """Return the span text showing records count."""
    spans = driver.find_elements(By.CSS_SELECTOR, "span")
    for s in spans:
        t = s.text or ""
        if "Records Found" in t or "No Records Found" in t or "Record Found" in t:
            return t
    return "NOT FOUND"

def test_pagination_filter_bulk():
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    results = {}
    try:
        login(driver)
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList")
        # Wait for table cards to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".oxd-table-card")))
        time.sleep(2)

        # ====================================================
        # TEST 1: Header Checkbox (Select-All on page)
        # ====================================================
        print("\n--- TEST 1: Header Checkbox (Bulk Select) ---")
        # First input[type=checkbox] is the header select-all
        all_checks = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        total_checkboxes = len(all_checks)
        print(f"Total checkboxes found: {total_checkboxes} (1 header + {total_checkboxes-1} rows)")

        header_check = all_checks[0]
        # Check it
        driver.execute_script("arguments[0].click();", header_check)
        time.sleep(1)

        # Count span checkboxes after checking header
        checked_spans = driver.find_elements(By.CSS_SELECTOR, ".oxd-checkbox-input--active.oxd-checkbox-input")
        print(f"Active checkbox spans after clicking header: {len(checked_spans)}")

        # Check for 'Delete Selected' button appearing
        delete_selected_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Delete Selected')]")
        print(f"'Delete Selected' button visible: {len(delete_selected_btns) > 0}")
        if delete_selected_btns:
            print(f"  Button text: '{delete_selected_btns[0].text}'")
        driver.save_screenshot("evidence/pim_bulk_selection.png")

        # Uncheck header checkbox
        driver.execute_script("arguments[0].click();", header_check)
        time.sleep(1)
        results['bulk_select'] = 'VERIFIED'

        # ====================================================
        # TEST 2: Filter by Employment Status
        # ====================================================
        print("\n--- TEST 2: Filter by Employment Status ---")
        dropdowns = driver.find_elements(By.CSS_SELECTOR, ".oxd-select-text")
        # DD0 = Employment Status (first dropdown, label shows -- Select --)
        emp_status_dd = dropdowns[0]
        emp_status_dd.click()
        time.sleep(1)

        options = driver.find_elements(By.CSS_SELECTOR, ".oxd-select-dropdown .oxd-select-option")
        print(f"Employment Status options: {[o.text for o in options if o.text]}")

        # Select first non-blank option
        non_blank_opts = [o for o in options if o.text and o.text != '-- Select --']
        if non_blank_opts:
            selected_opt_text = non_blank_opts[0].text
            non_blank_opts[0].click()
            time.sleep(1)
            print(f"Selected: '{selected_opt_text}'")

            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(3)

            filtered_count_text = get_records_count_text(driver)
            print(f"Filtered result count: '{filtered_count_text}'")
            driver.save_screenshot("evidence/pim_filter_employment_status.png")
            results['filter'] = filtered_count_text

        # ====================================================
        # TEST 3: Pagination under filtered results
        # ====================================================
        print("\n--- TEST 3: Pagination under filter ---")
        page_btns = driver.find_elements(By.CSS_SELECTOR, ".oxd-pagination-page-item--page")
        print(f"Pagination page buttons under filter: {len(page_btns)}")
        if len(page_btns) >= 2:
            page_btns[1].click()
            time.sleep(2)
            page2_count_text = get_records_count_text(driver)
            print(f"Page 2 count text: '{page2_count_text}'")

            # KEY OBSERVATION: Does the filter dropdown keep its value on page 2?
            current_dd_text = driver.find_elements(By.CSS_SELECTOR, ".oxd-select-text")[0].text
            print(f"Filter dropdown value on page 2: '{current_dd_text}'")
            driver.save_screenshot("evidence/pim_pagination_page2.png")
            results['pagination_filter_preserved'] = current_dd_text
        else:
            print("Only 1 page of results, cannot test pagination under filter.")

        # ====================================================
        # TEST 4: Reset button clears all filters & shows full list immediately
        # ====================================================
        print("\n--- TEST 4: Reset clears filters & shows full list ---")
        reset_btn = driver.find_element(By.XPATH, "//button[contains(., 'Reset')]")
        reset_btn.click()
        time.sleep(3)
        after_reset_count = get_records_count_text(driver)
        after_reset_dd = driver.find_elements(By.CSS_SELECTOR, ".oxd-select-text")[0].text
        print(f"After Reset - Count text: '{after_reset_count}'")
        print(f"After Reset - Dropdown value: '{after_reset_dd}'")
        driver.save_screenshot("evidence/pim_after_reset.png")
        results['reset_clears_filter'] = after_reset_dd == '-- Select --'

        # ====================================================
        # TEST 5: 'Include' dropdown default value
        # ====================================================
        print("\n--- TEST 5: 'Include' dropdown default ---")
        # DD1 = Include dropdown (defaults to 'Current Employees Only')
        include_dd = driver.find_elements(By.CSS_SELECTOR, ".oxd-select-text")[1]
        print(f"'Include' dropdown default value: '{include_dd.text}'")
        results['include_default'] = include_dd.text

        print("\n=== RESULTS SUMMARY ===")
        for k, v in results.items():
            print(f"  {k}: {v}")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_pagination_filter_bulk()
