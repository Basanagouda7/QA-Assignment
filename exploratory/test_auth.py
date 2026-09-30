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
    driver.implicitly_wait(5)
    return driver

def run_auth_tests():
    driver = get_driver()
    results = []
    
    try:
        print("[TEST] Navigating to OrangeHRM...")
        driver.get("https://opensource-demo.orangehrmlive.com/")
        wait = WebDriverWait(driver, 15)
        
        # 1. Page title and form presence
        wait.until(EC.presence_of_element_located((By.NAME, "username")))
        results.append({
            "step": "Page Load",
            "title": driver.title,
            "url": driver.current_url,
            "status": "PASS" if "OrangeHRM" in driver.title else "FAIL"
        })
        print(f"Loaded page: {driver.title} at {driver.current_url}")
        
        # 2. Empty submission
        login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        time.sleep(1)
        err_elements = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        err_texts = [e.text for e in err_elements if e.text]
        results.append({
            "step": "Empty Credentials",
            "errors": err_texts,
            "count": len(err_texts),
            "status": "PASS" if len(err_texts) == 2 and all("Required" in t for t in err_texts) else "FAIL"
        })
        print(f"Empty credentials validation: {err_texts}")
        driver.save_screenshot("evidence/auth_empty_credentials.png")
        
        # 3. Invalid credentials
        user_input = driver.find_element(By.NAME, "username")
        pass_input = driver.find_element(By.NAME, "password")
        user_input.send_keys("invalidUser123")
        pass_input.send_keys("wrongpass999")
        login_btn.click()
        
        alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".oxd-alert-content-text")))
        alert_text = alert.text
        results.append({
            "step": "Invalid Credentials",
            "alert": alert_text,
            "status": "PASS" if "Invalid credentials" in alert_text else "FAIL"
        })
        print(f"Invalid credentials response: {alert_text}")
        driver.save_screenshot("evidence/auth_invalid_credentials.png")
        
        # 4. Valid Login
        user_input = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
        pass_input = driver.find_element(By.NAME, "password")
        # Clear fields
        user_input.send_keys(Keys.CONTROL + "a")
        user_input.send_keys(Keys.DELETE)
        pass_input.send_keys(Keys.CONTROL + "a")
        pass_input.send_keys(Keys.DELETE)
        
        user_input.send_keys("Admin")
        pass_input.send_keys("admin123")
        login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        
        # Verify landing on Dashboard
        wait.until(EC.url_contains("/dashboard/index"))
        time.sleep(2)
        dashboard_header = driver.find_element(By.CSS_SELECTOR, ".oxd-topbar-header-breadcrumb").text
        results.append({
            "step": "Valid Login",
            "url": driver.current_url,
            "header": dashboard_header,
            "status": "PASS" if "Dashboard" in dashboard_header else "FAIL"
        })
        print(f"Valid login successful, landing on: {dashboard_header} ({driver.current_url})")
        driver.save_screenshot("evidence/dashboard_landing.png")
        
        # 5. Session and Logout
        user_dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".oxd-userdropdown-tab")))
        user_dropdown.click()
        time.sleep(1)
        logout_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Logout']")))
        logout_link.click()
        wait.until(EC.url_contains("/auth/login"))
        results.append({
            "step": "Logout Flow",
            "url": driver.current_url,
            "status": "PASS" if "/auth/login" in driver.current_url else "FAIL"
        })
        print("Logout verified successfully.")
        driver.save_screenshot("evidence/auth_logout.png")
        
        # 6. Back button after logout (Session Security)
        driver.back()
        time.sleep(2)
        back_url = driver.current_url
        print(f"After browser BACK: {back_url}")
        # Check if dashboard is restored or redirected back to login
        is_secured = "/auth/login" in back_url or len(driver.find_elements(By.NAME, "username")) > 0
        results.append({
            "step": "Back Button Session Test",
            "url": back_url,
            "status": "PASS" if is_secured else "FAIL",
            "observation": "Redirects or maintains login prompt upon back navigation" if is_secured else "User sees cached/unauthorized dashboard"
        })
        driver.save_screenshot("evidence/auth_back_navigation.png")
        
    finally:
        driver.quit()
        
    return results

def test_auth():
    results = run_auth_tests()
    for r in results:
        assert r["status"] == "PASS", f"Step failed: {r}"

if __name__ == "__main__":
    res = run_auth_tests()
    print("\n--- AUTH TEST RESULTS ---")
    for r in res:
        print(r)
