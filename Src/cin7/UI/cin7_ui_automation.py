from Src.access import cin7_username, cin7_password
from Src.helpers.file_helpers import get_header_list
from Src.helpers.ui_helpers import *
from Src.cin7.UI.cin7_locators import *


def login(driver, username, password):
	clear_and_send_keys(driver, LOGIN_USERNAME, username)
	clear_and_send_keys(driver, LOGIN_PASSWORD, password)
	click_and_wait(driver, LOGIN_PASSWORD_SUBMIT)
	wait_for_user_input()
	wait_for_element(driver, SEARCH_BUTTON)

def cin7_get_ui_aged_report():
	driver = setup_webdriver()
	try:
		open_page(driver, CIN7_AGED_INVENTORY_URL)
		login(driver, cin7_username(), cin7_password())
		return get_aged_report(driver)
	finally:
		close(driver)

def get_aged_report(driver):
	clear_and_send_keys(driver, START_DATE_FIELD, "01-01-2000")
	click_and_wait(driver, SEARCH_BUTTON)
	click_and_wait(driver, REPORT_DOWLOAD_CSV)
	df = wait_and_rename_downloaded_file(output_folder_path()+"downloads", "cin7_aged_report")
	df = trim_aged_report(df, get_header_list('cin7_aged_trim'))
	return df

def trim_aged_report(df, trim_list):
	"""
	Removes rows from the DataFrame where the 'Product' column's value contains any substring from the specified trim_list
	and where the 'Qty' column is 5 or less.

	Parameters:
	df (pd.DataFrame): The DataFrame to process.
	trim_list (list): A list of substrings to be removed from the DataFrame.

	Returns:
	pd.DataFrame: A DataFrame with the specified rows removed.
	"""
	# Check if 'Product' and 'Qty' are in the DataFrame
	if 'Product' not in df.columns:
		raise ValueError("The DataFrame does not contain a 'Product' column.")
	if 'Qty' not in df.columns:
		raise ValueError("The DataFrame does not contain a 'Qty' column.")

	# Define a function to check if any substrings are contained in the product name
	def contains_any_substring(product_name):
		return any(substring.lower() in product_name.lower() for substring in trim_list)

	# Filter out rows where 'Product' contains any substring from trim_list
	filtered_df = df[~df['Product'].apply(contains_any_substring)]

	# Further filter to exclude rows where 'Qty' is 5 or less
	filtered_df = filtered_df[filtered_df['Qty'] > 5]

	return filtered_df