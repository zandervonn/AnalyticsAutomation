import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import tkinter as tk

from Src.GUI.tkinter_app import CustomDialog


def open_page(driver, url):
	driver.get(url)
	time.sleep(2)  # Adjust the sleep time if necessary

def click_and_wait(driver, xpath, wait_time=10):
	element = WebDriverWait(driver, wait_time).until(
		EC.element_to_be_clickable((By.XPATH, xpath))
	)
	element.click()
	time.sleep(2) #todo remove sleeps

def close(driver):
	driver.quit()

def wait_for_element(driver, xpath, wait_time=50):
	WebDriverWait(driver, wait_time).until(
		EC.visibility_of_element_located((By.XPATH, xpath))
	)

def get_element_text(driver, xpath):
	return driver.find_element(By.XPATH, xpath).text

def wait_for_table_data(driver, table, timeout=30):
	data_locator = (By.XPATH, table)

	# Wait for the presence of the element
	WebDriverWait(driver, timeout).until(
		EC.presence_of_element_located(data_locator)
	)

def extract_table_data(driver, table_xpath):
	table = driver.find_element(By.XPATH, table_xpath)
	data = []

	# Extract column headers
	headers = table.find_elements(By.XPATH, './/thead/tr/th/button')
	header_row = [header.text.split('\n')[-1] for header in headers]
	data.append(header_row)

	# Extract table body data
	for row in table.find_elements(By.XPATH, './/tbody/tr'):
		row_data = []
		cells = row.find_elements(By.XPATH, './/th | .//td')
		for cell in cells:
			row_data.append(cell.text.split('\n')[0])
		data.append(row_data)

	# Convert to DataFrame
	df = pd.DataFrame(data[1:], columns=data[0])
	return df

def setup_webdriver():
	options = Options()
	options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
	# options.add_argument('--headless')  #todo not working in headless
	driver = webdriver.Chrome(options=options)
	return driver

def wait_for_user_input():
	print("waiting for user input")
	root = tk.Tk()
	root.withdraw()  # Hide the root window
	dialog = CustomDialog(root, "Input")
	user_input = dialog.result
	root.destroy()
	return user_input

def navigate_to(driver, url):
	driver.get(url)
	time.sleep(2)