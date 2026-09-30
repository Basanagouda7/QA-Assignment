import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_zero_records():
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
        
        search_id = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='Employee Id']/parent::div/following-sibling::div/input")))
        search_id.send_keys("NON_EXISTENT_9999")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        
        driver.save_screenshot("evidence/pim_zero_results.png")
        
        # Check toast messages
        toasts = driver.find_elements(By.CSS_SELECTOR, ".oxd-toast-content-text")
        print("Toasts found:", [t.text for t in toasts])
        
        # Check span texts
        spans = driver.find_elements(By.CSS_SELECTOR, ".orangehrm-horizontal-padding span")
        print("Header padding spans:", [s.text for s in spans if s.text])
        
        # Check table body or empty state
        body_text = driver.find_element(By.CSS_SELECTOR, ".orangehrm-container").text
        print("Container text:", repr(body_text))

    finally:
        driver.quit()

if __name__ == "__main__":
    test_zero_records()
