from Src import access
from Src.access import cin7_username, cin7_password
from Src.helpers.clean_csv_helpers import clean_numeric_columns
from Src.helpers.file_helpers import get_header_list
from Src.helpers.ui_helpers import *
from Src.cin7.UI.cin7_locators import *


def login(driver, username, password):
	clear_and_send_keys(driver, LOGIN_USERNAME, username)
	clear_and_send_keys(driver, LOGIN_PASSWORD, password)
	click_and_wait(driver, LOGIN_PASSWORD_SUBMIT)
	wait_for_user_input()
	wait_for_element(driver, LOGO)

def cin7_get_ui_reports(branch):

	dfs = {}

	driver = setup_webdriver()
	if branch == access.AUS:
		aged_url = CIN7_AGED_INVENTORY_URL_AUS
		stock_url = CIN7_STOCK_REPORT_URL_NZ
		dashboard_url = CIN7_DASHBOARD_URL_NZ
	else:  # branch == access.NZ:
		aged_url = CIN7_AGED_INVENTORY_URL_NZ
		stock_url = CIN7_STOCK_REPORT_URL_NZ
		dashboard_url = CIN7_DASHBOARD_URL_NZ

	try:
		open_page(driver, dashboard_url)
		if not is_element_visible(driver, LOGO):
			login(driver, cin7_username(), cin7_password())
		dfs['dashboard_report'] = get_dashboard_report(driver, dashboard_url)
		dfs['aged_report'] = get_aged_report(driver, aged_url)
		dfs['stock_report'] = get_stock_report(driver, stock_url)
		return dfs
	finally:
		close(driver)

def get_aged_report(driver, url):
	open_page(driver, url)
	clear_and_send_keys(driver, START_DATE_FIELD, "01-01-2000")
	click_and_wait(driver, SEARCH_BUTTON, use_js=True)
	wait_for_element(driver, AGE_REPORT_DATE_2000)
	time.sleep(3) #todo with dynamic wait
	before_download_time = time.time()
	click_and_wait(driver, REPORT_DOWLOAD_CSV)
	df = wait_and_rename_downloaded_file(output_folder_path()+"downloads", "cin7_aged_report", before_download_time)
	df = trim_aged_report(df, get_header_list('cin7_aged_trim'))
	return df

def get_stock_report(driver, url):
	open_page(driver, url)
	wait_for_element(driver, DOWNLOAD_STOCK_REPORT_BUTTON)
	before_download_time = time.time()
	click_and_wait(driver, DOWNLOAD_STOCK_REPORT_BUTTON)
	df = wait_and_rename_downloaded_file(output_folder_path()+"downloads", "cin7_stock_report", before_download_time)
	df = trim_stock_report(df)
	return df

def get_dashboard_report(driver, url):
	open_page(driver, url)
	wait_for_element(driver, DASHBOARD_DATA_BOX)
	df = get_dashboard_values(driver)
	df = clean_numeric_columns(df)
	return df

def get_dashboard_values(driver):
	data = {}

	# Find all elements with the class 'data-box-header extend'
	elements = get_element_list(driver, DASHBOARD_DATA_BOX)

	# Loop through each element to extract the title and value
	for element in elements:
		title = get_element_text(element, DASHBOARD_DATA_BOX_TITLE)
		value = get_element_text(element, DASHBOARD_DATA_BOX_VALUE)
		data[title] = [value]

	return pd.DataFrame(data)


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


def trim_stock_report(df):
	# Set the correct header row
	df.columns = df.iloc[0]
	df = df[1:]

	# Identify the 'Grand Total' row
	grand_total_row = df[df.iloc[:, 0] == 'Grand Total']

	if grand_total_row.empty:
		raise ValueError("No 'Grand Total' row found in the DataFrame.")

	# Extract relevant columns dynamically
	soh_retail_value = grand_total_row.iloc[0][df.columns.str.contains('Retail Stock Value|Retail Value', na=False)].values[0]
	soh_stock_value = grand_total_row.iloc[0][df.columns.str.contains('Stock Value', na=False)].values[0]
	soh = grand_total_row.iloc[0][df.columns.str.contains('SOH', na=False)].values[0]

	# Create a new DataFrame with the required values
	trimmed_df = pd.DataFrame({
		'SOH Retail Value': [soh_retail_value],
		'SOH Stock Value': [soh_stock_value],
		'SOH': [soh]
	})

	return trimmed_df