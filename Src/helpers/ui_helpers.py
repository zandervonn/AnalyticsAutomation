import json
import os
import time
import tkinter

import pandas as pd
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Src.access import output_folder_path, google_chrome_data_path


def open_page(driver, url):
	print(url)
	driver.get(url)

def click_and_wait(driver, xpath, wait_time=10, use_js=False):
	try:
		element = WebDriverWait(driver, wait_time).until(
			EC.element_to_be_clickable((By.XPATH, xpath))
		)
		if use_js:
			driver.execute_script("arguments[0].click();", element)
		else:
			element.click()
	except TimeoutException:
		print("Element not clickable at the path provided: {}".format(xpath))
	except Exception as e:
		print("Error clicking on element: {}".format(e))

def close(driver):
	driver.quit()

def wait_for_element(driver, xpath, wait_time=30):
	WebDriverWait(driver, wait_time).until(
		EC.visibility_of_element_located((By.XPATH, xpath))
	)

def get_element_text(driver, xpath):
	return driver.find_element(By.XPATH, xpath).text

def is_element_visible(driver, xpath, timeout=5):
	"""
	Checks if an element is visible within the given timeout.

	:param driver: The Selenium WebDriver instance.
	:param xpath: The XPath of the element to check.
	:param timeout: The maximum time to wait before giving up, in seconds.
	:return: True if the element is found within the timeout period, False otherwise.
	"""
	try:
		WebDriverWait(driver, timeout).until(
			EC.visibility_of_element_located((By.XPATH, xpath))
		)
		return True
	except TimeoutException:
		return False
	except Exception as e:
		print("Error while checking element visibility: {}".format(e))
		return False

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

	# Path to the user data directory
	# user_data_dir = google_chrome_data_path()

	# Ensure the directory exists
	# if not os.path.exists(user_data_dir):
	# 	os.makedirs(user_data_dir)

	# Specify the user data directory
	# options.add_argument(f"user-data-dir={user_data_dir}")

	# Set the download directory to the one returned by output_folder_path()
	prefs = {
		"download.default_directory": output_folder_path()+"downloads",
		"download.prompt_for_download": False,
		"download.directory_upgrade": True,
		"safebrowsing.enabled": True
	}
	options.add_experimental_option("prefs", prefs)

	# Set other capabilities as needed
	# options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

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

def refresh_until_visible(driver, xpath, timeout=120):
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

def wait_and_rename_downloaded_file(download_dir, new_filename, before_download_time, timeout=300, retry_interval=5, max_retries=5):
	downloaded_file_path = ''
	start_time = time.time()
	download_complete = False

	while not download_complete and (time.time() - start_time) < timeout:
		other_files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if not f.endswith('.crdownload')]
		new_files = [f for f in other_files if os.path.getmtime(f) > before_download_time]
		if new_files:
			downloaded_file_path = max(new_files, key=os.path.getmtime)
			download_complete = True
		time.sleep(retry_interval)

	if download_complete:
		# Ensure we get the final file after download completes by refreshing the file list
		time.sleep(1)  # Slight delay to ensure the file is completely written
		final_files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if not f.endswith('.crdownload')]
		final_new_files = [f for f in final_files if os.path.getmtime(f) > before_download_time]
		if final_new_files:
			downloaded_file_path = max(final_new_files, key=os.path.getmtime)

		file_extension = os.path.splitext(downloaded_file_path)[1]
		new_file_path = os.path.join(download_dir, new_filename + file_extension)
		os.replace(downloaded_file_path, new_file_path)  # This replaces the file if it exists
		print(f"File renamed to {new_file_path}")

		# Load the renamed file into a pandas DataFrame based on the file type
		if file_extension == '.csv':
			df = pd.read_csv(new_file_path)
		elif file_extension in ['.xls', '.xlsx']:
			df = pd.read_excel(new_file_path)
		else:
			raise ValueError("Unsupported file format for data processing.")
		return df
	else:
		raise Exception("Download did not complete within the allotted time.")


def wait_for_user_input():
	from Src.GUI.tkinter_app import CustomDialog
	print("waiting for user input")
	root = tkinter.Tk()
	root.withdraw()  # Hide the root window
	dialog = CustomDialog(root, "Input")
	user_input = dialog.result
	root.destroy()
	return user_input

def navigate_to(driver, url):
	driver.get(url)

def get_element_list(driver, xpath):
	"""
	Finds and returns a list of elements located by the given XPath.
	"""
	try:
		elements = WebDriverWait(driver, 10).until(
			EC.presence_of_all_elements_located((By.XPATH, xpath))
		)
		return elements
	except TimeoutException:
		print("Elements not found at the path provided: {}".format(xpath))
		return []
	except Exception as e:
		print("Error finding elements: {}".format(e))
		return []