"""
SauceDemo Automation Test Suite
Framework: Python + Selenium WebDriver + unittest
Target: https://www.saucedemo.com/
Tests: TC01-TC07 (mandatory) + additional edge cases
"""
import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ─── Configuration ─────────────────────────────────────────────────────────────
BASE_URL = "https://www.saucedemo.com/"
VALID_USER = "standard_user"
VALID_PASS = "secret_sauce"
LOCKED_USER = "locked_out_user"
INVALID_USER = "not_a_user"
INVALID_PASS = "wrong_password"
DRIVER_PATH = "drivers/chromedriver.exe"
EVIDENCE_DIR = "evidence/saucedemo"

os.makedirs(EVIDENCE_DIR, exist_ok=True)


# ─── Base Test Class ────────────────────────────────────────────────────────────
class SauceDemoBaseTest(unittest.TestCase):
    """Base class with driver setup/teardown and shared helpers."""

    def setUp(self):
        opt = Options()
        opt.add_argument('--headless=new')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        opt.add_argument('--disable-gpu')
        opt.add_argument('--window-size=1280,900')
        service = Service(DRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=opt)
        self.wait = WebDriverWait(self.driver, 15)
        self.driver.implicitly_wait(2)

    def tearDown(self):
        self.driver.quit()

    def login(self, username=VALID_USER, password=VALID_PASS):
        """Helper: log in with given credentials and wait for inventory page."""
        self.driver.get(BASE_URL)
        self.wait.until(EC.element_to_be_clickable((By.ID, "user-name"))).send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "login-button").click()

    def screenshot(self, name):
        self.driver.save_screenshot(f"{EVIDENCE_DIR}/{name}.png")

    def get_inventory_items(self):
        """Return all product item elements on the inventory page."""
        return self.driver.find_elements(By.CLASS_NAME, "inventory_item")

    def add_item_to_cart_by_index(self, index=0):
        """Add item at given index to cart."""
        items = self.get_inventory_items()
        btn = items[index].find_element(By.TAG_NAME, "button")
        item_name = items[index].find_element(By.CLASS_NAME, "inventory_item_name").text
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)
        return item_name


# ─── TC01: Login with Valid Credentials ────────────────────────────────────────
class TC01_ValidLogin(SauceDemoBaseTest):
    """TC01 — Login with valid credentials."""

    def test_valid_login(self):
        self.driver.get(BASE_URL)
        # Verify page title and login form
        self.assertEqual("Swag Labs", self.driver.title)
        self.wait.until(EC.visibility_of_element_located((By.ID, "login-button")))

        self.login()
        # Assert: redirected to /inventory.html
        self.wait.until(EC.url_contains("inventory.html"))
        self.assertIn("inventory.html", self.driver.current_url)

        # Assert: inventory title displayed
        title = self.driver.find_element(By.CLASS_NAME, "title").text
        self.assertEqual("Products", title)
        self.screenshot("tc01_valid_login_success")
        print("[TC01] PASS: Valid login navigated to Products page.")


# ─── TC02: Login with Invalid Credentials ──────────────────────────────────────
class TC02_InvalidLogin(SauceDemoBaseTest):
    """TC02 — Login with invalid credentials."""

    def test_invalid_user_and_password(self):
        self.driver.get(BASE_URL)
        self.wait.until(EC.element_to_be_clickable((By.ID, "user-name"))).send_keys(INVALID_USER)
        self.driver.find_element(By.ID, "password").send_keys(INVALID_PASS)
        self.driver.find_element(By.ID, "login-button").click()

        err = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-test='error']")))
        self.assertIn("Username and password do not match", err.text)
        self.assertEqual(BASE_URL, self.driver.current_url)
        self.screenshot("tc02_invalid_credentials_error")
        print(f"[TC02] PASS: Error shown: '{err.text}'")

    def test_locked_out_user(self):
        self.driver.get(BASE_URL)
        self.wait.until(EC.element_to_be_clickable((By.ID, "user-name"))).send_keys(LOCKED_USER)
        self.driver.find_element(By.ID, "password").send_keys(VALID_PASS)
        self.driver.find_element(By.ID, "login-button").click()

        err = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-test='error']")))
        self.assertIn("locked out", err.text)
        self.screenshot("tc02_locked_out_user")
        print(f"[TC02b] PASS: Locked-out user error: '{err.text}'")

    def test_empty_username(self):
        self.driver.get(BASE_URL)
        self.wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).click()

        err = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-test='error']")))
        self.assertIn("Username is required", err.text)
        self.screenshot("tc02_empty_username")
        print(f"[TC02c] PASS: Empty username error: '{err.text}'")


# ─── TC03: Product Listing Validation ──────────────────────────────────────────
class TC03_ProductListing(SauceDemoBaseTest):
    """TC03 — Product listing validation."""

    def setUp(self):
        super().setUp()
        self.login()
        self.wait.until(EC.url_contains("inventory.html"))

    def test_products_displayed(self):
        items = self.get_inventory_items()
        self.assertGreater(len(items), 0, "No inventory items found")
        self.assertEqual(6, len(items), "Expected 6 products on the page")
        self.screenshot("tc03_product_listing")
        print(f"[TC03] PASS: {len(items)} products displayed.")

    def test_each_product_has_name_price_button(self):
        items = self.get_inventory_items()
        for item in items:
            name = item.find_element(By.CLASS_NAME, "inventory_item_name").text
            price = item.find_element(By.CLASS_NAME, "inventory_item_price").text
            btn = item.find_element(By.TAG_NAME, "button")
            self.assertTrue(name, f"Item missing name: {item.get_attribute('outerHTML')[:100]}")
            self.assertTrue(price.startswith("$"), f"Price format wrong: '{price}'")
            self.assertEqual("Add to cart", btn.text)
        print(f"[TC03b] PASS: All {len(items)} items have name, price, and 'Add to cart' button.")

    def test_product_sort_price_low_to_high(self):
        sort_dd = self.driver.find_element(By.CLASS_NAME, "product_sort_container")
        sort_dd.click()
        options = self.driver.find_elements(By.CSS_SELECTOR, "select.product_sort_container option")
        option_texts = [o.text for o in options]
        print(f"[TC03c] Sort options available: {option_texts}")

        # Select 'Price (low to high)'
        from selenium.webdriver.support.ui import Select
        select = Select(self.driver.find_element(By.CLASS_NAME, "product_sort_container"))
        select.select_by_value("lohi")
        time.sleep(1)

        prices = [float(p.text.replace("$", ""))
                  for p in self.driver.find_elements(By.CLASS_NAME, "inventory_item_price")]
        self.assertEqual(prices, sorted(prices), "Products not sorted price low-to-high")
        self.screenshot("tc03c_sort_price_low_high")
        print(f"[TC03c] PASS: Prices sorted correctly: {prices}")


# ─── TC04: Add Product(s) to Cart ──────────────────────────────────────────────
class TC04_AddToCart(SauceDemoBaseTest):
    """TC04 — Add product(s) to cart."""

    def setUp(self):
        super().setUp()
        self.login()
        self.wait.until(EC.url_contains("inventory.html"))

    def test_add_single_item_updates_badge(self):
        # Badge should not exist before adding
        badges_before = self.driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")
        self.assertEqual(0, len(badges_before))

        item_name = self.add_item_to_cart_by_index(0)

        # Badge should show '1'
        badge = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "shopping_cart_badge")))
        self.assertEqual("1", badge.text)

        # Button text changes to 'Remove'
        items = self.get_inventory_items()
        btn_text = items[0].find_element(By.TAG_NAME, "button").text
        self.assertEqual("Remove", btn_text)

        self.screenshot("tc04_add_single_item")
        print(f"[TC04] PASS: Added '{item_name}', badge='1', button='Remove'.")

    def test_add_multiple_items_updates_badge(self):
        self.add_item_to_cart_by_index(0)
        self.add_item_to_cart_by_index(1)

        badge = self.driver.find_element(By.CLASS_NAME, "shopping_cart_badge")
        self.assertEqual("2", badge.text)
        self.screenshot("tc04_add_two_items")
        print(f"[TC04b] PASS: Two items in cart, badge='2'.")


# ─── TC05: Cart Content Validation ─────────────────────────────────────────────
class TC05_CartValidation(SauceDemoBaseTest):
    """TC05 — Cart content validation."""

    def setUp(self):
        super().setUp()
        self.login()
        self.wait.until(EC.url_contains("inventory.html"))

    def test_cart_shows_correct_items(self):
        # Add first two items
        name1 = self.add_item_to_cart_by_index(0)
        name2 = self.add_item_to_cart_by_index(1)

        # Navigate to cart
        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        self.wait.until(EC.url_contains("cart.html"))

        cart_items = self.driver.find_elements(By.CLASS_NAME, "cart_item")
        self.assertEqual(2, len(cart_items))

        cart_names = [i.find_element(By.CLASS_NAME, "inventory_item_name").text for i in cart_items]
        self.assertIn(name1, cart_names)
        self.assertIn(name2, cart_names)
        self.screenshot("tc05_cart_content")
        print(f"[TC05] PASS: Cart shows '{name1}' and '{name2}'.")

    def test_remove_item_from_cart(self):
        self.add_item_to_cart_by_index(0)
        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        self.wait.until(EC.url_contains("cart.html"))

        items_before = self.driver.find_elements(By.CLASS_NAME, "cart_item")
        self.assertEqual(1, len(items_before))

        # Remove item
        remove_btn = self.driver.find_element(By.CSS_SELECTOR, ".cart_item button")
        remove_btn.click()
        time.sleep(1)

        items_after = self.driver.find_elements(By.CLASS_NAME, "cart_item")
        self.assertEqual(0, len(items_after))

        # Badge should disappear
        badges = self.driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")
        self.assertEqual(0, len(badges))

        self.screenshot("tc05b_remove_from_cart")
        print("[TC05b] PASS: Item removed from cart, badge gone.")

    def test_empty_cart_has_no_items(self):
        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        self.wait.until(EC.url_contains("cart.html"))

        items = self.driver.find_elements(By.CLASS_NAME, "cart_item")
        self.assertEqual(0, len(items))
        self.screenshot("tc05c_empty_cart")
        print("[TC05c] PASS: Empty cart shows zero items.")


# ─── TC06: Checkout Happy Path ──────────────────────────────────────────────────
class TC06_CheckoutHappyPath(SauceDemoBaseTest):
    """TC06 — Complete checkout flow."""

    def setUp(self):
        super().setUp()
        self.login()
        self.wait.until(EC.url_contains("inventory.html"))
        self.add_item_to_cart_by_index(0)
        self.add_item_to_cart_by_index(1)
        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        self.wait.until(EC.url_contains("cart.html"))

    def test_checkout_complete_flow(self):
        # 1. Click Checkout
        checkout_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "checkout")))
        checkout_btn.click()
        self.wait.until(EC.url_contains("checkout-step-one"))

        # 2. Fill in customer info
        first_in = self.wait.until(EC.element_to_be_clickable((By.ID, "first-name")))
        first_in.clear()
        first_in.send_keys("Senior")
        self.driver.find_element(By.ID, "last-name").send_keys("QATester")
        self.driver.find_element(By.ID, "postal-code").send_keys("12345")
        continue_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "continue")))
        continue_btn.click()
        self.wait.until(EC.url_contains("checkout-step-two"))
        self.screenshot("tc06_checkout_step2_overview")

        # 3. Verify order summary page
        summary_label = self.driver.find_element(By.CLASS_NAME, "summary_info_label")
        self.assertIsNotNone(summary_label)

        # Verify item total and tax are present
        item_total = self.driver.find_element(By.CLASS_NAME, "summary_subtotal_label").text
        tax = self.driver.find_element(By.CLASS_NAME, "summary_tax_label").text
        total = self.driver.find_element(By.CLASS_NAME, "summary_total_label").text
        print(f"  Item Total: {item_total}")
        print(f"  Tax: {tax}")
        print(f"  Total: {total}")
        self.assertTrue(item_total.startswith("Item total:"))
        self.assertTrue(tax.startswith("Tax:"))
        self.assertTrue(total.startswith("Total:"))

        # 4. Finish order
        self.driver.find_element(By.ID, "finish").click()
        self.wait.until(EC.url_contains("checkout-complete"))

        # 5. Verify order confirmation
        confirm_header = self.driver.find_element(By.CLASS_NAME, "complete-header").text
        self.assertEqual("Thank you for your order!", confirm_header)
        self.screenshot("tc06_checkout_complete")
        print(f"[TC06] PASS: Checkout completed. Confirmation: '{confirm_header}'")

    def test_checkout_validation_empty_fields(self):
        """Verify checkout step 1 validates required fields."""
        self.driver.find_element(By.ID, "checkout").click()
        self.wait.until(EC.url_contains("checkout-step-one"))
        self.driver.find_element(By.ID, "continue").click()

        err = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-test='error']")))
        self.assertIn("First Name is required", err.text)
        self.screenshot("tc06b_checkout_validation")
        print(f"[TC06b] PASS: Checkout step-1 validation: '{err.text}'")


# ─── TC07: Logout ───────────────────────────────────────────────────────────────
class TC07_Logout(SauceDemoBaseTest):
    """TC07 — Logout flow."""

    def setUp(self):
        super().setUp()
        self.login()
        self.wait.until(EC.url_contains("inventory.html"))

    def test_logout_redirects_to_login(self):
        # Open burger menu
        burger = self.wait.until(EC.element_to_be_clickable((By.ID, "react-burger-menu-btn")))
        burger.click()
        time.sleep(1)

        # Click Logout
        logout_link = self.wait.until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link")))
        self.driver.execute_script("arguments[0].click();", logout_link)
        self.wait.until(EC.url_to_be(BASE_URL))

        # Verify back on login page
        self.assertIn(BASE_URL, self.driver.current_url)
        self.wait.until(EC.visibility_of_element_located((By.ID, "login-button")))
        self.screenshot("tc07_logout")
        print("[TC07] PASS: Logout redirected to login page.")

    def test_cannot_access_inventory_after_logout(self):
        """Verify session is invalidated after logout."""
        # Logout first
        burger = self.wait.until(EC.element_to_be_clickable((By.ID, "react-burger-menu-btn")))
        burger.click()
        time.sleep(1)
        logout_link = self.wait.until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link")))
        self.driver.execute_script("arguments[0].click();", logout_link)
        self.wait.until(EC.url_to_be(BASE_URL))

        # Try direct navigation to inventory
        self.driver.get(BASE_URL + "inventory.html")
        time.sleep(1)
        current = self.driver.current_url
        # Should be redirected back to login
        self.assertEqual(BASE_URL, current,
                         f"Expected redirect to login after logout, got: {current}")
        self.screenshot("tc07b_post_logout_session_check")
        print(f"[TC07b] PASS: Post-logout inventory access redirects to login. URL: {current}")


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes in order
    for cls in [
        TC01_ValidLogin,
        TC02_InvalidLogin,
        TC03_ProductListing,
        TC04_AddToCart,
        TC05_CartValidation,
        TC06_CheckoutHappyPath,
        TC07_Logout,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    exit(0 if result.wasSuccessful() else 1)
