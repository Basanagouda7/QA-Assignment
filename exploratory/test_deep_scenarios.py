import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_driver():
    opt = Options()
    opt.add_argument('--headless=new')
    opt.add_argument('--no-sandbox')
    opt.add_argument('--disable-dev-shm-usage')
    opt.add_argument('--disable-gpu')
    opt.add_argument('--window-size=1920,1080')
    service = Service('drivers/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=opt)
    driver.implicitly_wait(6)
    return driver

def login(driver):
    driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
    wait = WebDriverWait(driver, 15)
    user_in = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
    pass_in = driver.find_element(By.NAME, "password")
    user_in.send_keys("Admin")
    pass_in.send_keys("admin123")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    wait.until(EC.url_contains("/dashboard/index"))

def test_deep():
    driver = get_driver()
    wait = WebDriverWait(driver, 15)
    try:
        print("[DEEP] Logging in...")
        login(driver)
        
        # ========================================================
        # SCENARIO 1: PIM Search Filter 'Reset' Button UX Behavior
        # ========================================================
        print("\n--- [SCENARIO 1] PIM Search Reset Behavior ---")
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList")
        time.sleep(2)
        
        search_id = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='Employee Id']/parent::div/following-sibling::div/input")))
        search_id.send_keys("00000_NON_EXISTENT")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        
        records_after_search = driver.find_element(By.XPATH, "//span[contains(., 'Record Found') or contains(., 'No Records Found')]").text
        print(f"Records with non-existent ID: '{records_after_search}'")
        
        # Click Reset
        reset_btn = driver.find_element(By.XPATH, "//button[contains(., 'Reset')]")
        reset_btn.click()
        time.sleep(2)
        
        # Check if table automatically refreshes or remains showing 'No Records Found' until Search is clicked
        records_after_reset = driver.find_element(By.XPATH, "//span[contains(., 'Record Found') or contains(., 'Records Found') or contains(., 'No Records Found')]").text
        print(f"Records immediately after clicking Reset: '{records_after_reset}'")
        driver.save_screenshot("evidence/pim_reset_behavior.png")

        # ========================================================
        # SCENARIO 2: Leave Module - Date Range Logic (To Date < From Date)
        # ========================================================
        print("\n--- [SCENARIO 2] Leave Date Range Validation ---")
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/leave/applyLeave")
        time.sleep(2)
        print("Leave apply URL:", driver.current_url)
        driver.save_screenshot("evidence/leave_apply_page.png")
        
        # Check if user has leave entitlement or see validation messages
        # Find From Date and To Date inputs
        date_inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder='yyyy-dd-mm']")
        if not date_inputs:
            date_inputs = driver.find_elements(By.CSS_SELECTOR, ".oxd-date-input input")
        print(f"Found {len(date_inputs)} date inputs on Leave Apply.")
        
        if len(date_inputs) >= 2:
            from_date = date_inputs[0]
            to_date = date_inputs[1]
            
            # Set From Date to 2026-12-25, To Date to 2026-12-20 (To < From)
            from_date.send_keys(Keys.CONTROL + "a")
            from_date.send_keys(Keys.DELETE)
            from_date.send_keys("2026-25-12")
            
            to_date.send_keys(Keys.CONTROL + "a")
            to_date.send_keys(Keys.DELETE)
            to_date.send_keys("2026-20-12")
            
            # Click outside
            driver.find_element(By.TAG_NAME, "h6").click()
            time.sleep(1)
            
            date_errs = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
            date_err_texts = [e.text for e in date_errs if e.text]
            print(f"Date inversion validation: {date_err_texts}")
            driver.save_screenshot("evidence/leave_date_inversion_validation.png")

        # ========================================================
        # SCENARIO 3: Admin Module - Add User Validation & Autocomplete Enforcement
        # ========================================================
        print("\n--- [SCENARIO 3] Admin Module - Add User Flow ---")
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/admin/saveSystemUser")
        time.sleep(2)
        print("Add User URL:", driver.current_url)
        driver.save_screenshot("evidence/admin_add_user_page.png")
        
        # Click Save immediately to see all mandatory fields
        save_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        save_btn.click()
        time.sleep(1)
        
        admin_errs = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        print(f"Mandatory errors on Add User: {[e.text for e in admin_errs if e.text]}")
        driver.save_screenshot("evidence/admin_add_user_mandatory.png")
        
        # Test Employee Name field autocomplete: Type arbitrary string without selecting hint
        emp_name_hint = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Type for hints...']")
        emp_name_hint.send_keys("FakeNonExistentEmployeeXYZ")
        time.sleep(2)
        
        # Click outside to see if it allows invalid employee or shows 'Invalid'
        driver.find_element(By.XPATH, "//label[text()='Username']").click()
        time.sleep(1)
        
        emp_err = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        print(f"Invalid employee name hint error: {[e.text for e in emp_err if e.text]}")
        driver.save_screenshot("evidence/admin_invalid_emp_hint.png")

        # Test Password rules: weak password vs confirmation mismatch
        pass_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        print(f"Password inputs found: {len(pass_inputs)}")
        if len(pass_inputs) >= 2:
            pass_inputs[0].send_keys("123") # short/weak
            pass_inputs[1].send_keys("456") # mismatch
            driver.find_element(By.XPATH, "//label[text()='Username']").click()
            time.sleep(1)
            
            pwd_errs = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
            print(f"Password validation messages: {[e.text for e in pwd_errs if e.text]}")
            driver.save_screenshot("evidence/admin_password_validation.png")

        # ========================================================
        # SCENARIO 4: Recruitment Module - Candidate Email & Attachment Validation
        # ========================================================
        print("\n--- [SCENARIO 4] Recruitment Module - Add Candidate Validation ---")
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/recruitment/addCandidate")
        time.sleep(2)
        print("Add Candidate URL:", driver.current_url)
        driver.save_screenshot("evidence/recruitment_add_candidate_page.png")
        
        # Test malformed email
        email_in = driver.find_element(By.XPATH, "//label[text()='Email']/parent::div/following-sibling::div/input")
        email_in.send_keys("not-an-email")
        driver.find_element(By.XPATH, "//label[text()='Full Name']").click()
        time.sleep(1)
        
        email_errs = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        print(f"Malformed email validation message: {[e.text for e in email_errs if e.text]}")
        driver.save_screenshot("evidence/recruitment_email_validation.png")
        
        # Test Contact Number with alphabetical characters
        phone_in = driver.find_element(By.XPATH, "//label[text()='Contact Number']/parent::div/following-sibling::div/input")
        phone_in.send_keys("ABCDEFGHIJ-NOT-PHONE")
        driver.find_element(By.XPATH, "//label[text()='Full Name']").click()
        time.sleep(1)
        phone_errs = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        print(f"Alphabetic phone validation message: {[e.text for e in phone_errs if e.text]}")
        driver.save_screenshot("evidence/recruitment_phone_validation.png")

        # ========================================================
        # SCENARIO 5: Dashboard Quick Launch & Sidebar Responsive Toggle
        # ========================================================
        print("\n--- [SCENARIO 5] Navigation, Collapse Sidebar, Responsive Layout ---")
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/dashboard/index")
        time.sleep(2)
        
        # Check sidebar collapse button
        collapse_btn = driver.find_element(By.CSS_SELECTOR, ".oxd-main-menu-button")
        print(f"Sidebar collapse button found: {collapse_btn.is_displayed()}")
        collapse_btn.click()
        time.sleep(1)
        
        # Check sidebar class after toggle
        aside = driver.find_element(By.CSS_SELECTOR, "aside.oxd-sidepanel")
        print(f"Aside class after toggle: '{aside.get_attribute('class')}'")
        driver.save_screenshot("evidence/dashboard_sidebar_collapsed.png")
        
        # Re-expand sidebar
        collapse_btn.click()
        time.sleep(1)
        print(f"Aside class after re-expand: '{aside.get_attribute('class')}'")
        
        # Check Quick Launch icons
        quick_launch_items = driver.find_elements(By.CSS_SELECTOR, ".orangehrm-quick-launch-icon")
        print(f"Quick launch icons count: {len(quick_launch_items)}")
        driver.save_screenshot("evidence/dashboard_quick_launch.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_deep()
