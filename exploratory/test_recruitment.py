import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_recruitment():
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

        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/recruitment/addCandidate")
        time.sleep(2)
        print("Recruitment Add Candidate URL:", driver.current_url)
        
        # Test 1: Empty submit to verify mandatory fields
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        
        errs = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        print("Mandatory fields on Add Candidate:", [e.text for e in errs if e.text])
        driver.save_screenshot("evidence/recruitment_mandatory_fields.png")

        # Test 2: Invalid Email Format
        email_in = driver.find_element(By.XPATH, "//label[text()='Email']/parent::div/following-sibling::div/input")
        email_in.send_keys("invalid-candidate-email-at-domain")
        driver.find_element(By.NAME, "firstName").click() # blur
        time.sleep(1)
        
        email_errs = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        print("Email format validation:", [e.text for e in email_errs if e.text])
        driver.save_screenshot("evidence/recruitment_email_format_error.png")

        # Test 3: Contact number with invalid characters (e.g. letters)
        phone_in = driver.find_element(By.XPATH, "//label[text()='Contact Number']/parent::div/following-sibling::div/input")
        phone_in.send_keys("INVALID_PHONE_NUMBER_TEXT")
        driver.find_element(By.NAME, "firstName").click() # blur
        time.sleep(1)
        
        phone_errs = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        print("Contact number validation (letters entered):", [e.text for e in phone_errs if e.text])
        driver.save_screenshot("evidence/recruitment_phone_letters.png")

        # Test 4: Can a candidate be saved with alphabetic phone number?
        first_in = driver.find_element(By.NAME, "firstName")
        last_in = driver.find_element(By.NAME, "lastName")
        first_in.send_keys("SeniorTester")
        last_in.send_keys("CandidateQA")
        email_in.send_keys(Keys.CONTROL + "a")
        email_in.send_keys(Keys.DELETE)
        email_in.send_keys(f"qa_{int(time.time())}@example.com")
        
        # Click Save with alphabetic contact number
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        print("URL after submitting with alphabetic phone number:", driver.current_url)
        toasts = [t.text for t in driver.find_elements(By.CSS_SELECTOR, ".oxd-toast-content-text")]
        print("Toasts on submitting alphabetic phone:", toasts)
        driver.save_screenshot("evidence/recruitment_phone_saved_behavior.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_recruitment()
