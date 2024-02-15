from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import csv

webdriver_path = 'C:\\Users\\Zander\\.wdm\\chromedriver\\72.0.3626.7\\win32\\chromedriver.exe'
target_url = 'https://google.com'

def setup_webdriver():
	options = Options()
	# options.add_argument('--headless')  # Run in headless mode
	driver = webdriver.Chrome(options=options)
	return driver

def navigate_to(driver, url):
	driver.get(url)
	time.sleep(2)

def extract_data(driver):
	data = []
	return data

def write_data_to_csv(data, file_path):
	with open(file_path, mode='w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(data.keys())
		writer.writerow(data.values())

def extract_vi(driver):
	navigate_to(driver, target_url)
	data = extract_data(driver)
# write_data_to_csv(data, output_csv_file)

def open_page(driver, url):
	driver.get(url)
	time.sleep(2)  # Adjust the sleep time if necessary

def click_and_wait(driver, xpath, wait_time=10):
	element = WebDriverWait(driver, wait_time).until(
		EC.element_to_be_clickable((By.XPATH, xpath))
	)
	element.click()
	time.sleep(2)

def set_report_and_timeframe(driver, report_name, date_range):
	click_and_wait(driver, f"//span[text()='Analytics']")
	click_and_wait(driver, f"//a[contains(@aria-label,'View the {report_name} report')]")
	click_and_wait(driver, "(//div[contains(@class, 'TimeControlsContainer')]//button[contains(@class, 'Polaris-Button')])[1]")
	click_and_wait(driver, f"//ul[@class='Polaris-Box Polaris-Box--listReset']/li[contains(@class, 'Polaris-OptionList-Option')]/button[contains(., '{date_range}')]")
	click_and_wait(driver, f"//span[text()='Apply']")

def extract_table_data(driver):
	table = driver.find_element(By.CSS_SELECTOR, 'table.Polaris-DataTable__Table')
	data = [[cell.text for cell in row.find_elements(By.CSS_SELECTOR, 'th, td')] for row in table.find_elements(By.CSS_SELECTOR, 'tr')]
	return data

def save_to_csv(data, file_name):
	df = pd.DataFrame(data[1:], columns=data[0])
	df.to_csv(file_name, index=False)

def close(driver):
	driver.quit()

def wait_for_element(driver, xpath, wait_time=50):
	WebDriverWait(driver, wait_time).until(
		EC.visibility_of_element_located((By.XPATH, xpath))
	)

def get_ui_analytics():
	driver = setup_webdriver()
	try:
		open_page(driver, 'https://admin.shopify.com/store/gelous/dashboards')
		wait_for_element(driver, "//span[text()='Analytics']")
		time.sleep(5)
		set_report_and_timeframe(driver, report_name='Online store sessions', date_range='Last 30 days')
		time.sleep(5)
		data = extract_table_data(driver)
		save_to_csv(data, 'gitignore\\sessions_output.csv')
		time.sleep(5)
		open_page(driver, 'https://admin.shopify.com/store/gelous/dashboards')
		set_report_and_timeframe(driver, report_name='Online store conversion rate', date_range='Last 30 days')
		time.sleep(5)
		data = extract_table_data(driver)
		save_to_csv(data, 'gitignore\\conversions_output.csv')

	finally:
		close(driver)
