import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_admin_add_user():
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

        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/admin/saveSystemUser")
        time.sleep(2)
        print("Admin Add User URL:", driver.current_url)
        
        # 1. Test short username boundary (< 5 chars)
        username_in = driver.find_element(By.XPATH, "//label[text()='Username']/parent::div/following-sibling::div/input")
        username_in.send_keys("adm") # 3 chars
        driver.find_element(By.XPATH, "//label[text()='Password']").click()
        time.sleep(1)
        
        user_err = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        print("Username boundary validation (< 5 chars):", [e.text for e in user_err if e.text])
        driver.save_screenshot("evidence/admin_username_boundary.png")

        # 2. Test duplicate username (Admin)
        username_in.send_keys(Keys.CONTROL + "a")
        username_in.send_keys(Keys.DELETE)
        username_in.send_keys("Admin")
        driver.find_element(By.XPATH, "//label[text()='Password']").click()
        time.sleep(2)
        
        dup_err = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        print("Duplicate username validation ('Admin'):", [e.text for e in dup_err if e.text])
        driver.save_screenshot("evidence/admin_duplicate_username.png")

        # 3. Test Invalid Employee Name in autocomplete
        emp_name_in = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Type for hints...']")
        emp_name_in.send_keys("NoSuchEmployeeEver_99")
        time.sleep(2)
        driver.find_element(By.XPATH, "//label[text()='Password']").click()
        time.sleep(1)
        
        emp_err = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        print("Invalid employee name validation:", [e.text for e in emp_err if e.text])
        driver.save_screenshot("evidence/admin_invalid_employee.png")

        # 4. Test Password complexity and mismatch
        pass_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        if len(pass_inputs) >= 2:
            pass_inputs[0].send_keys("simple") # too short & lacks number/symbol
            pass_inputs[1].send_keys("different") # mismatch
            driver.find_element(By.XPATH, "//label[text()='Username']").click()
            time.sleep(1)
            
            pwd_errs = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
            print("Password validation messages:", [e.text for e in pwd_errs if e.text])
            driver.save_screenshot("evidence/admin_password_rules.png")

        # 5. Test Cancel button behavior
        cancel_btn = driver.find_element(By.XPATH, "//button[contains(., 'Cancel')]")
        cancel_btn.click()
        time.sleep(2)
        print("URL after clicking Cancel:", driver.current_url)
        driver.save_screenshot("evidence/admin_cancel_nav.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_admin_add_user()
