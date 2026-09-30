"""
Fixed DOM inspection with proper explicit waits for Vue.js SPA table rendering.
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

def inspect_dom():
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    try:
        login(driver)

        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList")
        # Wait for the employee table cards to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".oxd-table-card")))
        time.sleep(2)

        # Screenshot for visual reference
        driver.save_screenshot("evidence/dom_pim_table_loaded.png")

        # Print page body classes/key elements
        body_html = driver.find_element(By.CSS_SELECTOR, ".oxd-table").get_attribute("outerHTML")
        print("Table HTML (first 1200 chars):", body_html[:1200])
        print("\n---")

        # Check all checkboxes
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        print(f"\nTotal checkboxes: {len(checkboxes)}")
        for i, cb in enumerate(checkboxes[:3]):
            print(f"  CB{i}: class='{cb.get_attribute('class')}' id='{cb.get_attribute('id')}'")

        # Check for header row structure
        header_rows = driver.find_elements(By.CSS_SELECTOR, ".oxd-table-row--header")
        print(f"\nHeader rows: {len(header_rows)}")
        if header_rows:
            print("  Header HTML:", header_rows[0].get_attribute("outerHTML")[:400])

        # Check all labels for filters
        labels = [l.text for l in driver.find_elements(By.TAG_NAME, "label") if l.text]
        print("\nAll labels:", labels)

        # Check Employment Status dropdown options
        emp_status_dropdowns = driver.find_elements(By.CSS_SELECTOR, ".oxd-select-wrapper")
        print(f"\nDropdown wrappers: {len(emp_status_dropdowns)}")
        for i, dd in enumerate(emp_status_dropdowns):
            print(f"  DD{i}: {dd.get_attribute('outerHTML')[:250]}")

        # Check 'Records Found' span
        spans = driver.find_elements(By.CSS_SELECTOR, "span")
        record_spans = [s for s in spans if "Records" in (s.text or "") or "Record" in (s.text or "")]
        print("\nRecord count spans:", [(s.tag_name, s.text) for s in record_spans])

    finally:
        driver.quit()

if __name__ == "__main__":
    inspect_dom()
