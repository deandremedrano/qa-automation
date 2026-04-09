import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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
    driver.get("https://the-internet.herokuapp.com/login")
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    username_field.send_keys("tomsmith")
    password_field.send_keys("SuperSecretPassword!")
    submit_button.click()
    success_message = WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "flash"), "secure area")
    )
    assert success_message

def test_invalid_credentials(driver):
    driver.get("https://the-internet.herokuapp.com/login")
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    username_field.send_keys("tomsmith")
    password_field.send_keys("wrong_password")
    submit_button.click()
    error_message = WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "flash"), "invalid")
    )
    assert error_message

def test_empty_fields(driver):
    driver.get("https://the-internet.herokuapp.com/login")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()
    error_message = WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "flash"), "invalid")
    )
    assert error_message

def test_logout(driver):
    driver.get("https://the-internet.herokuapp.com/login")
    driver.find_element(By.ID, "username").send_keys("tomsmith")
    driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "flash"), "secure area")
    )
    driver.find_element(By.LINK_TEXT, "Logout").click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    assert "login" in driver.current_url