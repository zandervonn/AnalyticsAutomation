import os
import time

import pandas as pd
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tkinter as tk

from Src.GUI.tkinter_app import CustomDialog
from Src.access import output_folder_path


def open_page(driver, url):
	driver.get(url)

def click_and_wait(driver, xpath, wait_time=10):
	element = WebDriverWait(driver, wait_time).until(
		EC.element_to_be_clickable((By.XPATH, xpath))
	)
	element.click()

def close(driver):
	driver.quit()

def wait_for_element(driver, xpath, wait_time=30):
	WebDriverWait(driver, wait_time).until(
		EC.visibility_of_element_located((By.XPATH, xpath))
	)

def get_element_text(driver, xpath):
	return driver.find_element(By.XPATH, xpath).text

def wait_for_table_data(driver, table, timeout=30):
	data_locator = (By.XPATH, table)

	try:
		# Wait for the presence of the element
		WebDriverWait(driver, timeout).until(
			EC.presence_of_element_located(data_locator)
		)
	except TimeoutException:
		# Refresh the page and try again
		driver.refresh()
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

	# Set the download directory to the one returned by output_folder_path()
	prefs = {
		"download.default_directory": output_folder_path().replace('/', '\\')+"downloads",
		"download.prompt_for_download": False,
		"download.directory_upgrade": True,
		"safebrowsing.enabled": True
	}
	options.add_experimental_option("prefs", prefs)

	# Set other capabilities as needed
	options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

	# Initialize the Chrome WebDriver with the configured options
	driver = webdriver.Chrome(options=options)
	return driver

def clear_and_send_keys(driver, xpath, text):
	"""
	Clears the content of the text input and then sends new keys.
	"""
	element = WebDriverWait(driver, 10).until(
		EC.element_to_be_clickable((By.XPATH, xpath))
	)
	element.clear()
	element.send_keys(text)

def refresh_until_visible(driver, xpath, timeout=60):
	"""
	Continuously refreshes the page until the specified element is visible.
	:param timeout: Maximum time to wait before giving up, in seconds.
	"""
	end_time = time.time() + timeout
	while True:
		try:
			if WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath))):
				return  # If the element is found and visible, exit the function
		except TimeoutException:
			pass  # If the element is not found within the wait time, pass and refresh

		driver.refresh()
		if time.time() > end_time:
			raise Exception(f"Timeout reached while waiting for element {xpath}")
		time.sleep(3)  # Wait for 5 seconds before refreshing again to reduce load

def wait_and_rename_downloaded_file(download_dir, new_filename, timeout=300):
	"""
	Waits for a download to complete in 'download_dir', renames the new file, overwrites if necessary,
	and returns the file as a pandas DataFrame.
	Assumes there's only one file being downloaded at the time.
	"""
	start_time = time.time()
	download_complete = False
	downloaded_file_path = None

	# Wait for the download to complete
	while not download_complete and (time.time() - start_time) < timeout:
		time.sleep(1)  # Check every second
		for fname in os.listdir(download_dir):
			if not fname.endswith('.crdownload'):
				downloaded_file_path = os.path.join(download_dir, fname)
				download_complete = True
				break

	if downloaded_file_path:
		# Construct the full path for the new filename
		new_file_path = os.path.join(download_dir, new_filename)
		os.replace(downloaded_file_path, new_file_path)  # This replaces the file if it exists
		print(f"File renamed to {new_file_path}")

		# Load the renamed file into a pandas DataFrame
		df = pd.read_csv(new_file_path)
		return df
	else:
		raise Exception("Download did not complete within the allotted time.")


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