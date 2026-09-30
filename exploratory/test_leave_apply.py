import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_leave_apply():
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

        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/leave/applyLeave")
        time.sleep(3)
        print("Leave apply page URL:", driver.current_url)
        
        # Check leave type dropdown options
        dropdowns = driver.find_elements(By.CSS_SELECTOR, ".oxd-select-text")
        print(f"Dropdowns found: {len(dropdowns)}")
        if dropdowns:
            dropdowns[0].click()
            time.sleep(1)
            options = driver.find_elements(By.CSS_SELECTOR, ".oxd-select-dropdown .oxd-select-option")
            print("Leave Type Options:", [o.text for o in options if o.text])
            if len(options) > 1:
                options[1].click()
                time.sleep(1)

        # Inspect date inputs
        date_inputs = driver.find_elements(By.CSS_SELECTOR, ".oxd-date-input input")
        print(f"Date inputs found: {len(date_inputs)}")
        if len(date_inputs) >= 2:
            from_d = date_inputs[0]
            to_d = date_inputs[1]
            
            # Type From Date: 2026-10-15
            from_d.send_keys(Keys.CONTROL + "a")
            from_d.send_keys(Keys.DELETE)
            from_d.send_keys("2026-10-15")
            
            # Type To Date: 2026-10-10 (earlier than From Date)
            to_d.send_keys(Keys.CONTROL + "a")
            to_d.send_keys(Keys.DELETE)
            to_d.send_keys("2026-10-10")
            
            # Trigger validation by clicking on header
            driver.find_element(By.TAG_NAME, "h6").click()
            time.sleep(1)
            
            errs = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
            print("Date validation messages (To Date < From Date):", [e.text for e in errs if e.text])
            driver.save_screenshot("evidence/leave_date_validation_verified.png")

            # Click Apply button to see form-level submission behavior
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_btn.click()
            time.sleep(2)
            
            errs_after_submit = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
            toasts_after_submit = [t.text for t in driver.find_elements(By.CSS_SELECTOR, ".oxd-toast-content-text")]
            print("Errors after submitting inverted dates:", [e.text for e in errs_after_submit if e.text])
            print("Toasts after submitting inverted dates:", toasts_after_submit)
            driver.save_screenshot("evidence/leave_submit_inverted_dates.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_leave_apply()
