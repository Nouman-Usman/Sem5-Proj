import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginSignupTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:5173/login")

    def tearDown(self):
        self.driver.quit()

    def test_login(self):
        driver = self.driver
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        email_input.send_keys("test@example.com")
        password_input.send_keys("password")
        login_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".user-home"))
        )
        self.assertIn("user-home", driver.current_url)
        print("Login test passed: Successfully logged in and navigated to user home page.")

    def test_signup(self):
        driver = self.driver
        driver.get("http://localhost:5173/login")
        
        # Click on the Sign Up button to switch to the signup form
        toggle_signup_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Sign Up']"))
        )
        toggle_signup_button.click()
        
        name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "name"))
        )
        email_input = driver.find_element(By.ID, "signup-email")
        password_input = driver.find_element(By.ID, "signup-password")
        role_client_radio = driver.find_element(By.ID, "client")
        signup_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        name_input.send_keys("Test User")
        email_input.send_keys("testuser@example.com")
        password_input.send_keys("password")
        role_client_radio.click()
        signup_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".login"))
        )
        self.assertIn("login", driver.current_url)
        print("Signup test passed: Successfully signed up and navigated to login page.")

if __name__ == "__main__":
    unittest.main()
