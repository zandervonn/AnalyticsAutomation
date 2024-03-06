from Src.helpers.cleanCsvHelpers import clean_df, clean_dfs, sort_by_date_column, sort_by_value_column
from Src.starshipit.StarshipitAPI import *
from Src.cin7.Cin7API import *
from Src.google.googleAutomation import *
from Src.helpers.fileHelpers import *
from Src.helpers.timeHelpers import *
from Src.meta.metaAutomation import *
from Src.shopify.shopifyautomation import *
from Src.shopify.shopify_csv_handeling import *
from Src.shopify.shopifyUiAutomation import *
from gitignore.access import *
from config import *

since, until = get_dates("today", "weeks", 1)

def main_get_and_build_timeframe_shopify_order_report():
	print("Getting Shopify orders")
	new_orders_json = get_shopify_orders_updated_after(shopify_api_key(), shopify_password(), shopify_url(), since)
	orders_df = pd.json_normalize(new_orders_json)
	cleaned_orders_df = shopify_clean_df(orders_df)
	cleaned_orders_df = clean_df(cleaned_orders_df, shopify_defined_subheaders_orders)
	save_df_to_csv(cleaned_orders_df, path_gen('shopify', 'orders', 'csv'))

def main_get_and_build_timeframe_shopify_customer_report():
	#todo get average order value old vs new customer
	#todo get just the number of current users
	print("Getting Shopify customers")
	new_customers_json = get_shopify_customers_updated_after(shopify_api_key(), shopify_password(), shopify_url(), since)
	customers_cleaned_json = clean_json(new_customers_json, shopify_defined_subheaders_customers)
	orders_df = pd.json_normalize(customers_cleaned_json)
	cleaned_customers_df = clean_df(orders_df, shopify_defined_subheaders_customers)
	cleaned_customers_df = sort_by_date_column(cleaned_customers_df, ['updated_at'])
	save_df_to_csv(cleaned_customers_df, path_gen('shopify', 'customers', 'csv'))

def main_update_shopify_customer_report():
	shopify_customer_path = path_gen('shopify', 'customers', 'csv')

	print("Getting Shopify customers")

	# Read the timestamp of the last run
	last_run_timestamp = get_last_run_timestamp()
	print(f"Last run timestamp: {last_run_timestamp}")

	# Get new report
	new_customers_json = get_shopify_customers_updated_after(shopify_api_key(), shopify_password(), shopify_url(), last_run_timestamp)

	# Clean new customer data
	new_customers_df = pd.json_normalize(new_customers_json)
	cleaned_new_customers_df = clean_df(new_customers_df, shopify_defined_subheaders_customers)

	# Load the old customer report
	old_customers_df = load_csv(shopify_customer_path)


	# Update the old customer report by merging and cleaning
	updated_customers_df = update_dataframe(old_customers_df, cleaned_new_customers_df, 'id')
	updated_customers_df = clean_df(updated_customers_df, shopify_defined_subheaders_customers)
	updated_customers_df = sort_by_date_column(updated_customers_df, 'updated_at')

	# Save the updated report
	save_df_to_csv(updated_customers_df, shopify_customer_path)

	# Update the last run timestamp
	timestamp = set_last_run_timestamp()
	print(f"Updated last run timestamp to: {timestamp}")

def main_update_shopify_order_report():
	shopify_order_path = path_gen('shopify', 'orders', 'csv')

	print("Getting Shopify orders")

	# Read the timestamp of the last run
	last_run_timestamp = get_last_run_timestamp()
	print(f"Last run timestamp: {last_run_timestamp}")

	# Get new report
	new_orders_json = get_shopify_orders_updated_after(shopify_api_key(), shopify_password(), shopify_url(), last_run_timestamp)

	# Clean new order data
	new_orders_df = pd.json_normalize(new_orders_json)
	cleaned_new_orders_df = shopify_orders_clean_df(new_orders_df)
	cleaned_new_orders_df = clean_df(cleaned_new_orders_df, shopify_defined_subheaders_orders)

	# Update the old order report by merging and cleaning
	old_orders_df = load_csv(shopify_order_path)
	updated_orders_df = update_dataframe(old_orders_df, cleaned_new_orders_df, 'order_number')
	updated_orders_df = clean_df(updated_orders_df, shopify_defined_subheaders_orders)
	updated_orders_df = sort_by_value_column(updated_orders_df, 'order_number')

	# Save the updated report
	save_df_to_csv(updated_orders_df, shopify_order_path)

	# Update the last run timestamp
	timestamp = set_last_run_timestamp()
	print(f"Updated last run timestamp to: {timestamp}")

def main_get_and_build_starshipit_report():
	print("Getting Starshipit")
	unshipped_orders = get_unshipped_orders(starshipit_api_key(), starshipit_subscription_key(), 2, since, until)
	shipped_orders = get_shipped_orders(starshipit_api_key(), starshipit_subscription_key(), 2, since, until)
	unmanifested_shipments = get_unmanifested_shipments(starshipit_api_key(), starshipit_subscription_key(), 2, since, until)
	recently_printed_shipments = get_recently_printed_shipments(starshipit_api_key(), starshipit_subscription_key(), 2, since, until)
	df = combine_orders_to_df(unshipped_orders, shipped_orders, unmanifested_shipments, recently_printed_shipments)
	cleaned_df = clean_df(df, starshipit_defined_subheaders)
	save_df_to_csv(cleaned_df, path_gen('starshipit', 'orders', 'csv'))

def get_and_build_google():
	print("Getting Google")
	credentials = get_credentials(google_credentials_path(), google_token_path())
	google_dfs = get_google_analytics_sheets(credentials, google_property_id(), since, until, google_defined_headers_dimensions, google_defined_headers_metrics)
	clean_google_dfs = clean_dfs(google_dfs, google_defined_headers_dimensions+google_defined_headers_metrics)
	save_df_to_excel(clean_google_dfs, path_gen('google'))

def get_and_build_facebook():
	print("Getting Facebook")
	facebook_df = get_meta_insights(meta_access_token(),  meta_facebook_id(),  facebook_insights_headers, since, until, -1)
	save_df_to_csv(facebook_df, path_gen('facebook', 'data', 'csv'))
	clean_facebook_df = clean_df(facebook_df, ["end_time"]+facebook_insights_headers)
	split_facebook_df = split_insights_to_sheets(clean_facebook_df, facebook_insights_pages)
	save_df_to_excel(split_facebook_df, path_gen('facebook'))

def get_and_build_instagram():
	print("Getting Instagram")
	insta_df = get_meta_insights(meta_access_token(), meta_insta_id(),instagram_insights_headers, since, until, -1)
	clean_insta_df = clean_df(insta_df,  ["end_time"]+instagram_insights_headers)
	save_df_to_csv(clean_insta_df, path_gen('instagram', 'data', 'csv'))

def get_and_build_cin7():
	print("Getting Cin7")
	data = get_cin7_data(cin7_api_key())
	data = pd.json_normalize(data)
	cleaned_df = clean_df(data, cin7_defined_subheaders)
	save_df_to_csv(cleaned_df, path_gen('cin7', 'data', 'csv'))

def excel_update():
	#todo keep a years worth of data
	csv_files = [
		path_gen('shopify', 'orders', 'csv'),
		path_gen('shopify', 'customers', 'csv'),
		path_gen('cin7', 'data', 'csv'),
		path_gen('starshipit', 'orders', 'csv'),
		path_gen('instagram', 'data', 'csv'),
		# path_gen('google', 'sessions', 'csv'),
		# path_gen('facebook', 'data', 'csv'),
	]
	csv_sheets_to_excel(csv_files, path_gen('compiled'))

def main():
	# main_get_and_build_timeframe_shopify_customer_report()
	# main_get_and_build_timeframe_shopify_order_report()
	#
	# main_get_and_build_starshipit_report()
	# get_and_build_cin7()
	# get_and_build_instagram()
	#
	# excel_update()
	#
	# get_and_build_facebook()
	# get_and_build_google()

	# update_files(os.path.join(access.FOLDER_PATH, 'output'), os.path.join(access.FOLDER_PATH, 'custom'))


	main_update_shopify_customer_report()
	# main_update_shopify_order_report()

if __name__ == '__main__':
	main()