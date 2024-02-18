from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def open_page(driver, url):
	driver.get(url)
	time.sleep(2)  # Adjust the sleep time if necessary

def click_and_wait(driver, xpath, wait_time=10):
	element = WebDriverWait(driver, wait_time).until(
		EC.element_to_be_clickable((By.XPATH, xpath))
	)
	element.click()
	time.sleep(2)

def close(driver):
	driver.quit()

def wait_for_element(driver, xpath, wait_time=50):
	WebDriverWait(driver, wait_time).until(
		EC.visibility_of_element_located((By.XPATH, xpath))
	)


def setup_webdriver():
	options = Options()
	# options.add_argument('--headless')  # Run in headless mode
	driver = webdriver.Chrome(options=options)
	return driver

def navigate_to(driver, url):
	driver.get(url)
	time.sleep(2)