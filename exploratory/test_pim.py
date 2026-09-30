import time
import os
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

def test_pim_module():
    driver = get_driver()
    findings = []
    wait = WebDriverWait(driver, 15)
    
    try:
        print("[PIM] Logging in...")
        login(driver)
        
        # Navigate to PIM
        pim_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='PIM']")))
        pim_menu.click()
        wait.until(EC.url_contains("/pim/viewEmployeeList"))
        print("[PIM] Landed on Employee List.")
        time.sleep(2)
        
        # 1. Inspect Search Filters & Reset behavior
        search_inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder='Type for hints...']")
        print(f"Employee hint inputs found: {len(search_inputs)}")
        
        # Check Employee List records count
        record_count_elem = driver.find_element(By.XPATH, "//span[contains(., 'Records Found') or contains(., 'Record Found')]")
        initial_records_text = record_count_elem.text
        print(f"Initial record count text: {initial_records_text}")
        driver.save_screenshot("evidence/pim_employee_list_initial.png")
        
        # 2. Add Employee - Mandatory field validation
        add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add')]")))
        add_btn.click()
        wait.until(EC.url_contains("/pim/addEmployee"))
        time.sleep(2)
        print("[PIM] Landed on Add Employee page.")
        
        # Capture default auto-generated Employee ID
        emp_id_input = driver.find_element(By.XPATH, "//label[text()='Employee Id']/parent::div/following-sibling::div/input")
        default_emp_id = emp_id_input.get_attribute("value")
        print(f"Default Employee ID suggested: '{default_emp_id}'")
        
        # Click Save without entering First Name or Last Name
        save_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        save_btn.click()
        time.sleep(1)
        
        errs = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        err_texts = [e.text for e in errs if e.text]
        print(f"Validation on empty Add Employee: {err_texts}")
        driver.save_screenshot("evidence/pim_add_emp_mandatory_validation.png")
        
        # 3. Test Boundary Values & Whitespace on Name fields
        first_name_input = driver.find_element(By.NAME, "firstName")
        last_name_input = driver.find_element(By.NAME, "lastName")
        
        # Enter only whitespace
        first_name_input.send_keys("   ")
        last_name_input.send_keys("   ")
        save_btn.click()
        time.sleep(1)
        errs_ws = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        err_texts_ws = [e.text for e in errs_ws if e.text]
        print(f"Whitespace-only name validation: {err_texts_ws}")
        
        # Test excessively long string (> 100 characters) on First Name
        first_name_input.send_keys(Keys.CONTROL + "a")
        first_name_input.send_keys(Keys.DELETE)
        long_str = "A" * 120
        first_name_input.send_keys(long_str)
        entered_val = first_name_input.get_attribute("value")
        print(f"Length of entered long First Name: {len(entered_val)} (Expected max length limit)")
        driver.save_screenshot("evidence/pim_name_length_limit.png")
        
        # 4. Create a valid test employee
        test_first = "SeniorQA"
        test_middle = "AutoTester"
        test_last = "Evaluation"
        test_custom_id = f"QA{int(time.time()) % 100000:05d}"
        
        first_name_input.send_keys(Keys.CONTROL + "a")
        first_name_input.send_keys(Keys.DELETE)
        first_name_input.send_keys(test_first)
        
        mid_name_input = driver.find_element(By.NAME, "middleName")
        mid_name_input.send_keys(test_middle)
        
        last_name_input.send_keys(Keys.CONTROL + "a")
        last_name_input.send_keys(Keys.DELETE)
        last_name_input.send_keys(test_last)
        
        emp_id_input.send_keys(Keys.CONTROL + "a")
        emp_id_input.send_keys(Keys.DELETE)
        emp_id_input.send_keys(test_custom_id)
        
        print(f"Submitting employee: {test_first} {test_last} with ID: {test_custom_id}")
        save_btn.click()
        
        # Wait for redirect to Personal Details page
        wait.until(EC.url_contains("/pim/viewPersonalDetails/empNumber"))
        time.sleep(3)
        print(f"Successfully created employee! Landed on: {driver.current_url}")
        driver.save_screenshot("evidence/pim_employee_created_personal_details.png")
        
        # 5. Verify Persistence & Edit details
        nickname_input = driver.find_element(By.XPATH, "//label[text()='Nickname']/parent::div/following-sibling::div/input")
        nickname_input.send_keys("SeniorTester")
        
        # Save personal details
        details_save_btn = driver.find_element(By.XPATH, "//h6[text()='Personal Details']/following::button[@type='submit'][1]")
        driver.execute_script("arguments[0].scrollIntoView(true);", details_save_btn)
        time.sleep(1)
        details_save_btn.click()
        
        # Check toast message
        toast = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".oxd-toast-content-text")))
        print(f"Toast message on edit save: '{toast.text}'")
        driver.save_screenshot("evidence/pim_edit_toast.png")
        time.sleep(3)
        
        # 6. Test Duplicate Employee ID validation
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/pim/addEmployee")
        wait.until(EC.url_contains("/pim/addEmployee"))
        time.sleep(2)
        
        first_name_input = driver.find_element(By.NAME, "firstName")
        last_name_input = driver.find_element(By.NAME, "lastName")
        emp_id_input = driver.find_element(By.XPATH, "//label[text()='Employee Id']/parent::div/following-sibling::div/input")
        
        first_name_input.send_keys("Duplicate")
        last_name_input.send_keys("TestUser")
        emp_id_input.send_keys(Keys.CONTROL + "a")
        emp_id_input.send_keys(Keys.DELETE)
        emp_id_input.send_keys(test_custom_id) # Duplicate ID!
        
        time.sleep(1)
        # Check for immediate inline validation or on blur
        first_name_input.click() # blur emp_id field
        time.sleep(1)
        
        dup_errs = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        dup_texts = [e.text for e in dup_errs if e.text]
        print(f"Duplicate Employee ID validation message: {dup_texts}")
        driver.save_screenshot("evidence/pim_duplicate_id_validation.png")
        
        # 7. Search for newly created employee in Employee List
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList")
        wait.until(EC.url_contains("/pim/viewEmployeeList"))
        time.sleep(2)
        
        search_id_input = driver.find_element(By.XPATH, "//label[text()='Employee Id']/parent::div/following-sibling::div/input")
        search_id_input.send_keys(test_custom_id)
        
        search_submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        search_submit.click()
        time.sleep(2)
        
        found_records = driver.find_elements(By.CSS_SELECTOR, ".oxd-table-card")
        print(f"Search by custom ID '{test_custom_id}' returned {len(found_records)} row(s).")
        driver.save_screenshot("evidence/pim_search_results.png")
        
        # 8. Reset filter test
        reset_btn = driver.find_element(By.XPATH, "//button[contains(., 'Reset')]")
        reset_btn.click()
        time.sleep(2)
        cleared_val = driver.find_element(By.XPATH, "//label[text()='Employee Id']/parent::div/following-sibling::div/input").get_attribute("value")
        print(f"Employee ID filter value after Reset: '{cleared_val}'")
        
        # 9. Clean up: Delete the test employee
        # Search again to isolate our record
        search_id_input = driver.find_element(By.XPATH, "//label[text()='Employee Id']/parent::div/following-sibling::div/input")
        search_id_input.send_keys(test_custom_id)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        
        delete_btn = driver.find_element(By.XPATH, "//div[@class='oxd-table-cell-actions']//button[i[contains(@class, 'bi-trash')]]")
        delete_btn.click()
        time.sleep(1)
        
        # Check confirmation modal
        modal_header = driver.find_element(By.CSS_SELECTOR, ".orangehrm-modal-header").text
        print(f"Delete confirmation modal header: {modal_header}")
        driver.save_screenshot("evidence/pim_delete_modal.png")
        
        # Confirm delete
        confirm_btn = driver.find_element(By.XPATH, "//button[contains(., 'Yes, Delete')]")
        confirm_btn.click()
        time.sleep(2)
        
        # Verify toast and table emptiness for this ID
        driver.save_screenshot("evidence/pim_after_delete.png")
        time.sleep(2)
        search_id_input = driver.find_element(By.XPATH, "//label[text()='Employee Id']/parent::div/following-sibling::div/input")
        search_id_input.send_keys(Keys.CONTROL + "a")
        search_id_input.send_keys(Keys.DELETE)
        search_id_input.send_keys(test_custom_id)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        
        empty_info = driver.find_elements(By.XPATH, "//span[contains(., 'No Records Found')]")
        print(f"Search after deletion confirmed: {'No Records Found' if empty_info else 'Record still present!'}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_pim_module()
