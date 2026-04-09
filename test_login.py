import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://the-internet.herokuapp.com/login"
VALID_USERNAME = "tomsmith"
VALID_PASSWORD = "SuperSecretPassword!"

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def test_valid_login(driver):
    driver.get(BASE_URL)
    driver.find_element(By.ID, "username").send_keys(VALID_USERNAME)
    driver.find_element(By.ID, "password").send_keys(VALID_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    success = driver.find_element(By.ID, "flash").text
    assert "secure area" in success.lower()
    print("TC001 PASSED - Valid login successful")

def test_invalid_username(driver):
    driver.get(BASE_URL)
    driver.find_element(By.ID, "username").send_keys("wronguser")
    driver.find_element(By.ID, "password").send_keys(VALID_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    error = driver.find_element(By.ID, "flash").text
    assert "invalid" in error.lower()
    print("TC002 PASSED - Invalid username shows error")

def test_invalid_password(driver):
    driver.get(BASE_URL)
    driver.find_element(By.ID, "username").send_keys(VALID_USERNAME)
    driver.find_element(By.ID, "password").send_keys("wrongpassword")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    error = driver.find_element(By.ID, "flash").text
    assert "invalid" in error.lower()
    print("TC003 PASSED - Invalid password shows error")

def test_empty_fields(driver):
    driver.get(BASE_URL)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    error = driver.find_element(By.ID, "flash").text
    assert "invalid" in error.lower()
    print("TC004 PASSED - Empty fields shows error")

def test_logout(driver):
    driver.get(BASE_URL)
    driver.find_element(By.ID, "username").send_keys(VALID_USERNAME)
    driver.find_element(By.ID, "password").send_keys(VALID_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    driver.find_element(By.CSS_SELECTOR, "a.button").click()
    assert "login" in driver.current_url
    print("TC005 PASSED - Logout successful")