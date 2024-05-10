from datetime import datetime

from Src.helpers.file_helpers import load_mapping
from Src.helpers.ui_helpers import *
from Src.starshipit.UI.starshipit_locators import *
from Src.access import starshipit_username, starshipit_password, employee_mapping_path, sending_address


def login(driver, username, password):
	driver.find_element(By.XPATH, LOGIN_USERNAME).send_keys(username)
	driver.find_element(By.XPATH, LOGIN_PASSWORD).send_keys(password)
	click_and_wait(driver, LOGIN_PASSWORD_SUBMIT)
	time.sleep(1)
	wait_for_element(driver, GENERATE_BUTTON)

def starshipit_get_ui_report(since, until, testing):
	driver = setup_webdriver()
	try:
		open_page(driver, STARSHIPIT_URL)
		login(driver, starshipit_username(), starshipit_password())
		return get_report(driver, since, until, testing)
	finally:
		close(driver)

def get_report(driver, since, until, testing=False):
	since = since.split("T")[0]
	until = until.split("T")[0]
	# Convert dates from "dd/mm/yyyy" to "mm/dd/yyyy"
	since = datetime.strptime(since, "%Y-%m-%d").strftime("%d/%m/%Y")
	until = datetime.strptime(until, "%Y-%m-%d").strftime("%d/%m/%Y")
	clear_and_send_keys(driver, START_DATE_FIELD, since)
	clear_and_send_keys(driver, END_DATE_FIELD, until)
	driver.find_element(By.XPATH, CHILD_ORDER_CHECKBOX).click()
	if not testing:
		click_and_wait(driver, GENERATE_BUTTON)
		time.sleep(1)
		refresh_until_visible(driver, REPORT_STATUS_READY)
		driver.find_element(By.XPATH, REPORT_DOWLOAD_CSV).click()
	else:
		wait_for_user_input()
	return wait_and_rename_downloaded_file(output_folder_path()+"downloads", "starshipit_package_report")

def process_starshipit_ui_report(df):
	rawData = process_handeling_dates(df.copy())

	dateAverages = process_handeling_dates_average(rawData.copy()).reset_index(drop=True)
	postage_info = calculate_postage(df).reset_index(drop=True)
	postage_types = calculate_postage_type(df).reset_index(drop=True)
	package_types = calculate_package_type(df).reset_index(drop=True)
	status_info = calculate_status(rawData.copy()).reset_index(drop=True)
	orders_items_info = calculate_orders_packed_items_picked(df).reset_index(drop=True)

	accounts_orders = pivot_orders_picked_by_day(df).reset_index(drop=True)
	accounts_items = pivot_items_picked_by_day(df).reset_index(drop=True)

	name_mapping = load_mapping(employee_mapping_path())
	accounts_orders = rename_and_aggregate_columns(accounts_orders, name_mapping)
	accounts_items = rename_and_aggregate_columns(accounts_items, name_mapping)

	full_address_df = create_full_address_df(df).reset_index(drop=True)

	page2 = pd.concat([dateAverages, postage_info, postage_types, package_types, status_info, orders_items_info], axis=1)

	# Create a dictionary with each DataFrame
	dfs = {
		'RawData': rawData,
		'SummaryPage': page2,
		'AccountsOrders': accounts_orders,
		'AccountsItems': accounts_items,
		'FullAddresses': full_address_df
	}

	return dfs

#if this fails testing is turned on and new report is not the expected report
def process_handeling_dates(df):
	df['Processing Time'] = df.apply(lambda row: calculate_days_between(row['Order Date'], row['Printed Date']), axis=1)
	df['Delivery Time'] = df.apply(lambda row: calculate_days_between(row['Printed Date'], row['Delivered Date']), axis=1)
	df['Handling Time'] = df.apply(lambda row: calculate_days_between(row['Order Date'], row['Delivered Date']), axis=1)
	df['Package Status'] = df.apply(status_label, axis=1)
	return df[['Order Date', 'Printed Date', 'Delivered Date', 'Processing Time', 'Delivery Time', 'Handling Time', 'Package Status']]

def process_handeling_dates_average(df):
	result = {
		'Processing Time': df['Processing Time'].mean(),
		'Delivery Time': df['Delivery Time'].mean(),
		'Handling Time': df['Handling Time'].mean()
	}
	return pd.DataFrame([result])

def calculate_postage(df):
	df['Postage Cost'] = df['Price']

	# Create a new column with NaNs for 'Postage Recovered'
	df['Postage Recovered'] = pd.NA

	# Set the total only in the first row
	df.loc[0, 'Postage Recovered'] = df['Price'].sum()

	# Sort the DataFrame by 'Postage Cost' in descending order before slicing
	df_sorted = df.sort_values(by='Postage Cost', ascending=False)

	return df_sorted[['Postage Cost', 'Postage Recovered']]

def calculate_postage_type(df):
	postage_type_count = df['Carrier'].value_counts().reset_index()
	postage_type_count.columns = ['Postage Type', 'Postage Type #']
	return postage_type_count

def calculate_package_type(df):
	package_type_count = df['Package Sent'].value_counts().reset_index()
	package_type_count.columns = ['Package Type', 'Package Type #']
	return package_type_count

def calculate_status(df):
	status_count = df['Package Status'].value_counts().reset_index()
	status_count.columns = ['Status', 'Status #']
	return status_count

def pivot_orders_picked_by_day(df):
	"""
	Create a pivot table that shows the count of orders by 'AccountName' for each day.

	Parameters:
	df (DataFrame): Input DataFrame with a 'Printed Date' and 'AccountName'.

	Returns:
	DataFrame: A pivot table with dates as rows, account names as columns, and counts of orders as values.
	"""
	df['Date'] = pd.to_datetime(df['Printed Date']).dt.date
	pivot_df = df.pivot_table(index='Date', columns='AccountName', values='Printed Date', aggfunc='size', fill_value=0)
	pivot_df = pivot_df.sort_values(by='Date', ascending=True)
	pivot_df = pivot_df.reset_index().tail(8)
	return pivot_df

def pivot_items_picked_by_day(df):
	"""
	Create a pivot table that sums the 'Items Picked' for each 'Date' and 'AccountName'.
	Assumes 'Item Skus' entries are semicolon-separated strings.

	Parameters:
	df (DataFrame): Input DataFrame with 'Order Date', 'AccountName', and 'Item Skus'.

	Returns:
	DataFrame: A pivot table with dates as rows, account names as columns, and sum of items picked as values.
	"""
	df['Date'] = pd.to_datetime(df['Printed Date']).dt.date
	df['Items Picked'] = df['Item Skus'].apply(lambda x: len(x.split(';')) if isinstance(x, str) else 0)
	pivot_df = df.pivot_table(index='Date', columns='AccountName', values='Items Picked', aggfunc='sum', fill_value=0)
	pivot_df = pivot_df.sort_values(by='Date', ascending=True)
	pivot_df = pivot_df.reset_index().tail(8)

	return pivot_df


def calculate_orders_packed_items_picked(df):
	# Convert 'Printed Date' to datetime and strip time, ensuring format is 'Y-M-D'
	df['Orders Packed Date'] = pd.to_datetime(df['Printed Date']).dt.date

	# Calculate the number of orders packed
	orders_packed_count = df.groupby('Orders Packed Date').size().reset_index(name='Orders Packed')

	# Calculate the number of items picked
	df['Items Picked'] = df['Item Skus'].apply(lambda x: len(x.split(';')) if isinstance(x, str) else 1)
	items_picked_count = df.groupby('Orders Packed Date')['Items Picked'].sum().reset_index()

	# Merge the counts
	result = orders_packed_count.merge(items_picked_count, on='Orders Packed Date', how='outer')

	# Include 'Items Picked Date' as duplicate of 'Orders Packed Date'
	result['Items Picked Date'] = result['Orders Packed Date']

	# Sort by date in descending order to see the most recent entries first
	result = result.sort_values(by='Orders Packed Date', ascending=True).reset_index(drop=True)

	return result

def create_full_address_df(df):
	# Concatenate the address components into a full address
	df['Full Address'] = df[['Street', 'Suburb', 'State', 'Postcode', 'Country']].apply(
		lambda row: ', '.join(str(val) if not pd.isna(val) else '' for val in row),
		axis=1
	)

	df['Sending Address'] = sending_address()  # assuming sending_address() returns a string

	# Select only the relevant columns
	address_df = df[['Street', 'Suburb', 'State', 'Postcode', 'Country', 'Full Address', 'Sending Address']]
	return address_df

def calculate_days_between(d1, d2):
	"""Calculate the difference in days between two dates."""
	if pd.isnull(d1) or pd.isnull(d2):
		return None
	return (pd.to_datetime(d2) - pd.to_datetime(d1)).days

def status_label(row):
	"""Determine package status based on date availability."""
	if pd.isnull(row['Delivered Date']):
		return 'Still in Transit'
	return 'Delivered'

def rename_and_aggregate_columns(df, mapping):
	"""
	Rename and aggregate DataFrame columns based on a mapping. Sum columns if they are mapped to the same new name.
	Remove columns that are mapped to 'REMOVE'. Capitalize the first letter of each column header.

	Parameters:
	df (DataFrame): The DataFrame to process.
	mapping (dict): A dictionary mapping old column names to new names or 'REMOVE' to indicate removal.

	Returns:
	DataFrame: The modified DataFrame with renamed, aggregated, and properly capitalized columns.
	"""
	# Trim and handle removal
	df.columns = df.columns.str.strip()
	columns_to_drop = [col for col, new_name in mapping.items() if new_name == "REMOVE"]

	# Reverse mapping for aggregation
	reverse_mapping = {}
	for old_col, new_col in mapping.items():
		if new_col != "REMOVE":
			reverse_mapping.setdefault(new_col, []).append(old_col)

	# Aggregate columns
	for new_col, old_cols in reverse_mapping.items():
		existing_cols = [col for col in old_cols if col in df.columns]
		if len(existing_cols) > 1:
			df[new_col] = df[existing_cols].sum(axis=1)
			columns_to_drop.extend(existing_cols)
		elif len(existing_cols) == 1:
			df.rename(columns={existing_cols[0]: new_col}, inplace=True)

	# Drop columns
	df.drop(columns=set(columns_to_drop), inplace=True, errors='ignore')

	# Capitalize first letter of each header
	df.columns = df.columns.str.capitalize()

	return df

def add_open_orders_to_starshipit(processed_df, open_orders):
	"""
	Adds the open order count to an existing DataFrame under the 'SummaryPage' sheet.
	Inserts 'Open Orders' in the 'Status' column and the count in the 'Status #' column.

	Parameters:
	processed_df (dict): Dictionary of DataFrames, key is the sheet name.
	open_orders (int): The count of open orders to add.

	Returns:
	dict: Updated dictionary of DataFrames with the open order count added.
	"""
	# Ensure that the SummaryPage exists in the processed DataFrame dictionary
	if 'SummaryPage' not in processed_df:
		print("SummaryPage not found in the DataFrame.")
		return processed_df

	# Access the DataFrame for the SummaryPage
	summary_df = processed_df['SummaryPage']

	# Ensure 'Status' and 'Status #' columns exist, if not create them and initialize as empty
	if 'Status' not in summary_df.columns:
		summary_df['Status'] = None
	if 'Status #' not in summary_df.columns:
		summary_df['Status #'] = None

	# Find the first available index to add 'Open Orders' and the count
	idx = (summary_df['Status'].isnull() | summary_df['Status'].eq('')).idxmax()
	summary_df.at[idx, 'Status'] = 'Open Orders'
	summary_df.at[idx, 'Status #'] = open_orders

	# Save the updated DataFrame back into the dictionary
	processed_df['SummaryPage'] = summary_df

	return processed_df