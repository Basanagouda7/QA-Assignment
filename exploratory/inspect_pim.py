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

def inspect_pim():
    driver = get_driver()
    wait = WebDriverWait(driver, 15)
    try:
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        user_in = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
        pass_in = driver.find_element(By.NAME, "password")
        user_in.send_keys("Admin")
        pass_in.send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("/dashboard/index"))

        # Navigate to PIM personal details of empNumber 207 or latest
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewPersonalDetails/empNumber/207")
        time.sleep(3)
        print("URL:", driver.current_url)
        driver.save_screenshot("evidence/pim_personal_details_inspect.png")
        
        # Print all visible labels
        labels = driver.find_elements(By.TAG_NAME, "label")
        print("Labels found on Personal Details:")
        for l in labels:
            if l.text:
                print(f" - {l.text}")

        # Test duplicate Employee ID on Add Employee
        print("\n--- Testing Duplicate Employee ID Validation ---")
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/pim/addEmployee")
        time.sleep(2)
        emp_id_in = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='Employee Id']/parent::div/following-sibling::div/input")))
        emp_id_in.send_keys(Keys.CONTROL + "a")
        emp_id_in.send_keys(Keys.DELETE)
        emp_id_in.send_keys("QA20156") # The ID we just created
        
        # Click outside to trigger validation
        driver.find_element(By.NAME, "firstName").click()
        time.sleep(1)
        
        errs = driver.find_elements(By.CSS_SELECTOR, ".oxd-input-group__message")
        print("Duplicate Employee ID validation messages:")
        for e in errs:
            print(f" - {e.text}")
        driver.save_screenshot("evidence/pim_duplicate_id_evidence.png")

        # Test Search & Filter on Employee List
        print("\n--- Testing Employee List Search & Table Behavior ---")
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList")
        time.sleep(2)
        
        # Search by exact Employee ID
        search_id = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='Employee Id']/parent::div/following-sibling::div/input")))
        search_id.send_keys("QA20156")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        
        cards = driver.find_elements(By.CSS_SELECTOR, ".oxd-table-card")
        print(f"Rows returned for QA20156: {len(cards)}")
        if cards:
            print("Row text:", cards[0].text.replace("\n", " | "))
        driver.save_screenshot("evidence/pim_search_found_record.png")

        # Delete the test employee
        if cards:
            del_icon = cards[0].find_element(By.CSS_SELECTOR, ".bi-trash")
            del_icon.click()
            time.sleep(1)
            confirm_del = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Yes, Delete')]")))
            confirm_del.click()
            time.sleep(2)
            print("Deleted test employee QA20156.")
            driver.save_screenshot("evidence/pim_delete_confirmed.png")

        # Test Sorting and Pagination on Employee List
        print("\n--- Testing Table Sorting & Pagination ---")
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList")
        time.sleep(2)
        
        # Check sort icons on headers
        headers = driver.find_elements(By.CSS_SELECTOR, ".oxd-table-header .oxd-table-header-cell")
        header_names = [h.text for h in headers if h.text]
        print(f"Table headers: {header_names}")
        
        # Check sortable headers
        sort_icons = driver.find_elements(By.CSS_SELECTOR, ".oxd-table-header-sort")
        print(f"Sortable header icons count: {len(sort_icons)}")
        
        # Test pagination buttons
        pagination_items = driver.find_elements(By.CSS_SELECTOR, ".oxd-pagination-page-item")
        print(f"Pagination items found: {len(pagination_items)}")
        for p in pagination_items:
            print(f" - Page button: '{p.text}'")

    finally:
        driver.quit()

if __name__ == "__main__":
    inspect_pim()
