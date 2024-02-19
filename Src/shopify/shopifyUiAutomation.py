from Src.helpers.UIHelpers import *
from Src.helpers.csvHelpers import *
import pandas as pd
import time

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

def process_order_sessions_table_data(raw_data):
	# Create an empty DataFrame to hold processed data
	processed_data = pd.DataFrame()

	# Iterate over each row of raw data
	for row in raw_data:
		# Create a new row for processed data
		processed_row = {}
		for i, cell in enumerate(row):
			if '\n' in cell:  # Check if the cell contains newline characters
				# Split the cell into 'before' and 'after' based on '\n'
				before, after = cell.split('\n')[:2]  # Exclude percentage changes
				# Add 'before' and 'after' to the processed row
				processed_row[f'Column{i}_Before'] = before
				processed_row[f'Column{i}_After'] = after
			else:
				# Directly add data to the processed row
				processed_row[f'Column{i}'] = cell
		# Append the processed row to the DataFrame
		processed_data = processed_data.append(processed_row, ignore_index=True)

	return processed_data



def get_ui_analytics():
	driver = setup_webdriver()
	try:
		open_page(driver, 'https://admin.shopify.com/store/gelous/dashboards')
		wait_for_element(driver, "//span[text()='Analytics']")
		time.sleep(5)
		set_report_and_timeframe(driver, report_name='Online store sessions', date_range='Last 30 days')
		time.sleep(5)
		data = extract_table_data(driver)
		save_to_csv(data, '../gitignore/shopify/sessions_output.csv')
		time.sleep(5)
		open_page(driver, 'https://admin.shopify.com/store/gelous/dashboards')
		set_report_and_timeframe(driver, report_name='Online store conversion rate', date_range='Last 30 days')
		time.sleep(5)
		data = extract_table_data(driver)
		save_to_csv(data, '../gitignore/shopify/conversions_output.csv')

	finally:
		close(driver)
