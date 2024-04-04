from Src.helpers.UIHelpers import *
from Src.helpers.cleanCsvHelpers import clean_keep_first_row
from Src.helpers.csvHelpers import *
from Src.shopify.UI.locators import *
from gitignore.access import shopify_ui_username, shopify_ui_password


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

	for query_name, query in query_tuples:
		url = f_string(SHOPIFY_CUSTOMERS_URL_TEMPLATE, query)
		print(url)
		open_page(driver, url)
		wait_for_element(driver, CUSTOMER_COUNT_NUM)
		num_count = get_element_text(driver, CUSTOMER_COUNT_NUM)
		percent_count = get_element_text(driver, CUSTOMER_COUNT_PERCENT)
		data.append({
			'type': query_name,
			'count': num_count,
			'percent': percent_count
		})

	df = pd.DataFrame(data)
	return "Customer Metrics", df

def set_report_and_timeframe(driver, date_range):
	wait_for_table_data(driver, TABLE_CELL)
	click_and_wait(driver, REPORT_TIME_CONTOLLER_BUTTON)
	click_and_wait(driver, f_string(REPORT_TIME_CONTROLLER_TEMPLATE, date_range))
	click_and_wait(driver, APPLY_BUTTON)

def get_ui_analytics(reports, since, until):
	driver = setup_webdriver()
	dfs = {}  # Initialize a dictionary to store the dataframes
	try:
		open_page(driver, SHOPIFY_URL)
		login(driver, shopify_ui_username(), shopify_ui_password())
		for report in reports:
			if report == 'customer_count':
				query_tuples = [
					("Active", "last_order_date%20%3E%3D%20-12m"),
					("Australian", "customer_countries%20CONTAINS%20%27AU%27"),
					("Total", "")  # For total customers
				]
				name, df = get_customers(driver, query_tuples)
				dfs[name] = df
			else:
				name, df = get_report(driver, report, since, until)
				dfs[name] = df
	finally:
		close(driver)
	# wait_for_user_input() #for testing
	return dfs  # Return the dictionary of dataframes
