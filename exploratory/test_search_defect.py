import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_employee_id_search_defect():
    opt = Options()
    opt.add_argument('--headless=new')
    opt.add_argument('--no-sandbox')
    opt.add_argument('--disable-dev-shm-usage')
    opt.add_argument('--disable-gpu')
    opt.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(service=Service('drivers/chromedriver.exe'), options=opt)
    wait = WebDriverWait(driver, 15)
    try:
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        wait.until(EC.element_to_be_clickable((By.NAME, "username"))).send_keys("Admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("/dashboard/index"))

        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList")
        time.sleep(2)
        
        # Test 1: Search with Alphanumeric string 'NON_EXISTENT_9999'
        search_id = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='Employee Id']/parent::div/following-sibling::div/input")))
        search_id.send_keys("TEST_ABC_123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        
        toasts1 = driver.find_elements(By.CSS_SELECTOR, ".oxd-toast-content-text")
        toasts1_text = [t.text for t in toasts1]
        span1 = [s.text for s in driver.find_elements(By.CSS_SELECTOR, ".orangehrm-horizontal-padding span") if s.text]
        print("Test 1 (Alphanumeric 'TEST_ABC_123'):")
        print(" - Toasts:", toasts1_text)
        print(" - Span:", span1)
        driver.save_screenshot("evidence/pim_search_alphanumeric_error.png")
        
        # Clear field and test Test 2: Search with purely numeric non-existent ID '999999'
        time.sleep(3) # let toast fade
        search_id.send_keys(Keys.CONTROL + "a")
        search_id.send_keys(Keys.DELETE)
        search_id.send_keys("999999")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        
        toasts2 = driver.find_elements(By.CSS_SELECTOR, ".oxd-toast-content-text")
        toasts2_text = [t.text for t in toasts2]
        span2 = [s.text for s in driver.find_elements(By.CSS_SELECTOR, ".orangehrm-horizontal-padding span") if s.text]
        body2 = driver.find_element(By.CSS_SELECTOR, ".orangehrm-container").text
        print("\nTest 2 (Numeric '999999'):")
        print(" - Toasts:", toasts2_text)
        print(" - Span:", span2)
        print(" - Container text:", repr(body2))
        driver.save_screenshot("evidence/pim_search_numeric_no_records.png")

        # Test 3: Search by Employee Name with non-existent name
        driver.find_element(By.XPATH, "//button[contains(., 'Reset')]").click()
        time.sleep(2)
        name_hint = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Type for hints...']")
        name_hint.send_keys("NonExistentEmployee999")
        time.sleep(2)
        name_err = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        print("\nTest 3 (Employee Name hint non-existent):")
        print(" - Inline errors on hint input:", [e.text for e in name_err if e.text])
        driver.save_screenshot("evidence/pim_name_hint_invalid.png")
        
        # Click search with non-existent name
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        span3 = [s.text for s in driver.find_elements(By.CSS_SELECTOR, ".orangehrm-horizontal-padding span") if s.text]
        toasts3 = [t.text for t in driver.find_elements(By.CSS_SELECTOR, ".oxd-toast-content-text")]
        print(" - After Search click with invalid name hint:")
        print("   Toasts:", toasts3)
        print("   Span:", span3)
        driver.save_screenshot("evidence/pim_search_invalid_name.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_employee_id_search_defect()
