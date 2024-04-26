from Src.helpers.file_helpers import load_employee_mapping
from Src.helpers.ui_helpers import *
from Src.starshipit.UI.starshipit_locators import *
from Src.access import starshipit_username, starshipit_password, employee_mapping_path


def login(driver, username, password):
	driver.find_element(By.XPATH, LOGIN_USERNAME).send_keys(username)
	driver.find_element(By.XPATH, LOGIN_PASSWORD).send_keys(password)
	click_and_wait(driver, LOGIN_PASSWORD_SUBMIT)
	time.sleep(1)
	wait_for_element(driver, GENERATE_BUTTON)

def starshipit_get_ui_report(since, until):
	driver = setup_webdriver()
	try:
		open_page(driver, STARSHIPIT_URL)
		login(driver, starshipit_username(), starshipit_password())
		return get_report(driver, since, until)
	finally:
		close(driver)

def get_report(driver, since, until):
	clear_and_send_keys(driver, START_DATE_FIELD, since.split("T")[0])
	clear_and_send_keys(driver, END_DATE_FIELD, until.split("T")[0])
	driver.find_element(By.XPATH, CHILD_ORDER_CHECKBOX).click()
	# click_and_wait(driver, GENERATE_BUTTON)
	time.sleep(1)
	refresh_until_visible(driver, REPORT_STATUS_READY)
	driver.find_element(By.XPATH, REPORT_DOWLOAD_CSV).click()
	return wait_and_rename_downloaded_file(output_folder_path()+"downloads", "starshipit_package_report.csv")

def process_report(df):
	rawData = process_handeling_dates(df.copy())

	dateAverages = process_handeling_dates_average(rawData.copy())
	postage_info = calculate_postage(df)
	postage_types = calculate_postage_type(df)
	package_types = calculate_package_type(df)
	status_info = calculate_status(rawData.copy())
	orders_items_info = calculate_orders_packed_items_picked(df).head(7).reset_index(drop=True)

	accounts_orders = pivot_orders_picked_by_day(df).head(7)
	accounts_items = pivot_items_picked_by_day(df).head(7)

	name_mapping = load_employee_mapping(employee_mapping_path())
	accounts_orders = rename_columns_using_mapping(accounts_orders, name_mapping)
	accounts_items = rename_columns_using_mapping(accounts_items, name_mapping)

	page2 = pd.concat([dateAverages, postage_info, postage_types, package_types, status_info, orders_items_info], axis=1)

	# Create a dictionary with each DataFrame
	dfs = {
		'RawData': rawData,
		'SummaryPage': page2,
		'AccountsOrders': accounts_orders,
		'AccountsItems': accounts_items
	}

	return dfs

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

	# Create a new column with NaNs
	df['Postage Recovered'] = pd.NA

	# Set the total only in the first row
	df.loc[0, 'Postage Recovered'] = df['Price'].sum()

	return df[['Postage Cost', 'Postage Recovered']]

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
	# Normalize the date to remove the time component and convert to 'YYYY-MM-DD' string format
	df['Printed Date'] = pd.to_datetime(df['Printed Date']).dt.date

	# Pivot the table to get counts of AccountName per Date
	pivot_df = df.pivot_table(index='Printed Date', columns='AccountName', aggfunc='size', fill_value=0)

	# Flatten the MultiIndex columns and join with the index (Date)
	pivot_df.columns = [col for col in pivot_df.columns]  # Flatten MultiIndex
	pivot_df = pivot_df.reset_index()  # Make sure 'Date' is a column
	pivot_df = pivot_df.sort_values(by='Printed Date', ascending=False)  # Sort by date descending

	return pivot_df

def pivot_items_picked_by_day(df):
	# Ensure 'Order Date' is a datetime and 'AccountName' is a string
	df['Date'] = pd.to_datetime(df['Order Date']).dt.date
	df['AccountName'] = df['AccountName'].astype(str)

	# Count the number of SKUs in each 'Item Skus' entry, assuming they are separated by semicolons
	df['Items Picked'] = df['Item Skus'].apply(lambda x: len(x.split(';')) if isinstance(x, str) else 0)

	# Create a pivot table that sums the 'Items Picked' for each 'Date' and 'AccountName'
	pivot_df = df.pivot_table(index='Date', columns='AccountName', values='Items Picked', aggfunc='sum', fill_value=0)

	# Flatten the MultiIndex columns and join with the index (Date)
	pivot_df.columns = [col for col in pivot_df.columns]  # Flatten MultiIndex
	pivot_df = pivot_df.reset_index()  # Make sure 'Date' is a column
	pivot_df = pivot_df.sort_values(by='Date', ascending=False)  # Sort by date descending

	return pivot_df


def calculate_orders_packed_items_picked(df):
	# Convert dates and format them without the time
	df['Orders Packed Date'] = pd.to_datetime(df['Order Date']).dt.date
	orders_packed_count = df.groupby('Orders Packed Date').size().reset_index(name='Orders Packed')

	df['Items Picked'] = df['Item Skus'].apply(lambda x: len(x.split(';')) if isinstance(x, str) else 1)
	items_picked_count = df.groupby('Orders Packed Date')['Items Picked'].sum().reset_index()

	# Merge using the corrected column names
	result = orders_packed_count.merge(items_picked_count, on='Orders Packed Date', how='outer')
	result = result.sort_values(by='Orders Packed Date', ascending=False)  # Sort by date descending
	return result

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

def rename_columns_using_mapping(df, mapping):
	# Trim all the white spaces in the column names
	trimmed_column_names = {col: col.strip() for col in df.columns}
	df = df.rename(columns=trimmed_column_names)

	# Use the mapping to rename the columns
	new_column_names = {col: mapping.get(col, col) for col in df.columns}
	df = df.rename(columns=new_column_names)

	return df