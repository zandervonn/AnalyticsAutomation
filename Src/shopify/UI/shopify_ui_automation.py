from datetime import datetime

from Src.helpers.ui_helpers import *
from Src.helpers.clean_csv_helpers import clean_keep_first_row
from Src.helpers.csv_helpers import *
from Src.shopify.UI.shopify_locators import *
from Src.access import shopify_ui_username, shopify_ui_password


def login(driver, username, password):
	driver.find_element(By.XPATH, LOGIN_USERNAME).send_keys(username)
	click_and_wait(driver, LOGIN_USERNAME_SUBMIT)
	wait_for_element(driver, LOGIN_PASSWORD)
	driver.find_element(By.XPATH, LOGIN_PASSWORD).send_keys(password)
	click_and_wait(driver, LOGIN_PASSWORD_SUBMIT)
	wait_for_element(driver, ANALYTICS)

def get_report(driver, report_name, since, until):
	url = f_string(SHOPIFY_REPORTS_URL_TEMPLATE, report_name, since, until)
	print(url)
	open_page(driver, url)
	wait_for_table_data(driver, TABLE_CELL)
	data = extract_table_data(driver, TABLE)
	data = clean_keep_first_row(data)

	table_name = get_element_text(driver, HEADER_TEXT)
	output_file = table_name.replace(" ", "_")

	return output_file, data

def get_customers(driver, query_tuples):
	data = []
	total_customers = 0
	new_customers = 0

	for query_name, query in query_tuples:
		url = f_string(SHOPIFY_CUSTOMERS_URL_TEMPLATE, query)
		print(url)
		open_page(driver, url)
		wait_for_element(driver, CUSTOMER_COUNT_NUM)
		num_count = get_element_text(driver, CUSTOMER_COUNT_NUM).replace(',', '')
		percent_count = get_element_text(driver, CUSTOMER_COUNT_PERCENT).replace('%', '')

		# Store counts numerically
		data.append({
			'type': query_name,
			'count': int(num_count),
			'percent': float(percent_count)
		})

		if query_name == "Total":
			total_customers = int(num_count)
		elif query_name == "New":
			new_customers = int(num_count)

	df = pd.DataFrame(data)

	# Calculate additional metrics
	active_customers = df[df['type'] == 'Active']['count'].values[0]
	non_active_customers = total_customers - active_customers
	ratio_active_customers = (active_customers / total_customers * 100) if total_customers else 0

	# Calculate prior period base
	prior_period_customer_base = total_customers - new_customers

	# Reformat DataFrame
	result_df = pd.DataFrame({
		'Prior Period Customer Base': [prior_period_customer_base],
		'Current Customer Base': [total_customers],
		'Australia Customers in NZ Shopify': df[df['type'] == 'Australian']['count'].values[0],
		'Increase in Customer Base': [new_customers],
		'Active Customers': [active_customers],
		'Non-Active Customers': [non_active_customers],
		'Ratio - Active Customers': [f"{ratio_active_customers:.2f}%"]
	})

	return "Customer Metrics", result_df

def set_report_and_timeframe(driver, date_range):
	wait_for_table_data(driver, TABLE_CELL)
	click_and_wait(driver, REPORT_TIME_CONTOLLER_BUTTON)
	click_and_wait(driver, f_string(REPORT_TIME_CONTROLLER_TEMPLATE, date_range))
	click_and_wait(driver, APPLY_BUTTON)

def handle_customer_count(driver):
	query_tuples = [
		("Active", "last_order_date%20%3E%3D%20-12m"),
		("Australian", "customer_countries%20CONTAINS%20%27AU%27"),
		("New", "customer_added_date%20>%3D%20-7d%20"),
		("Total", "")  # For total customers
	]
	name, df = get_customers(driver, query_tuples)
	return name, df

def get_ui_analytics(reports, since, until):
	driver = setup_webdriver()
	dfs = {}  # Initialize a dictionary to store the dataframes
	try:
		open_page(driver, SHOPIFY_URL)
		login(driver, shopify_ui_username(), shopify_ui_password())
		for report in reports:
			if report == 'customer_count':
				name, df = handle_customer_count(driver)
				dfs[name] = df
			elif report == 2792653102:
				date = datetime.today().strftime('%Y-%m-%d')
				name, df = get_report(driver, report, "2000-01-01", date)
				dfs[name] = df
				wait_for_user_input()
			else:
				name, df = get_report(driver, report, since, until)
				dfs[name] = df
	finally:
		close(driver)

	return dfs  # Return the dictionary of dataframes

def combine_shopify_reports(dfs):
	# Extract the specific dataframes
	df_conversion = dfs.get('Online_store_conversion_over_time')
	df_sales = dfs.get('Sales_over_time')

	# Clean and convert 'Sessions' and 'Sessions converted' columns to numeric
	df_conversion['Sessions'] = pd.to_numeric(df_conversion['Sessions'].str.replace(',', ''), errors='coerce')
	df_conversion['Sessions converted'] = pd.to_numeric(df_conversion['Sessions converted'].str.replace(',', ''), errors='coerce')

	# Merge the two dataframes on 'Day'
	df_combined = df_conversion.merge(df_sales, on='Day', suffixes=('', '_sales'))

	# Select and rename the required columns
	df_final = df_combined[['Day', 'Sessions', 'Added to cart', 'Reached checkout', 'Orders', 'Conversion rate', 'Total sales']].copy()

	# Ensure 'Orders' is numeric, removing commas and converting to numeric
	df_final['Orders'] = pd.to_numeric(df_final['Orders'].str.replace(',', ''), errors='coerce')

	# Recalculate the conversion rate
	df_final.loc[:, 'Conversion rate'] = df_final['Orders'] / df_final['Sessions']

	# Format conversion rate as percentage
	df_final.loc[:, 'Conversion rate'] = df_final['Conversion rate'].apply(lambda x: f"{x:.2%}")

	# Replace the two original dataframes with the new combined dataframe in the dictionary
	dfs['conversions_over_time'] = df_final  # Add the new combined dataframe
	dfs.pop('Online_store_conversion_over_time', None)  # Remove the original conversion dataframe
	dfs.pop('Sales_over_time', None)  # Remove the original sales dataframe

	# Return the modified dictionary of dataframes
	return dfs