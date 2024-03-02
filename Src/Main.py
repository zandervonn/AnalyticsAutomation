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

def main_get_and_build_shopify_order_report():
	new_orders_json = get_shopify_orders_updated_after(shopify_api_key(), shopify_password(), shopify_url(), since)
	orders_df = pd.json_normalize(new_orders_json)
	cleaned_orders_df = shopify_clean_df(orders_df)
	cleaned_orders_df = clean_df(cleaned_orders_df, shopify_defined_subheaders_orders)
	save_df_to_csv(cleaned_orders_df, path_gen('shopify', 'orders', 'clean', 'csv'))

def main_get_and_build_shopify_customer_report():
	#todo get last updated date
	#todo get average order value old vs new customer
	#todo get just the number of current users
	new_customers_json = get_shopify_customers(shopify_api_key(), shopify_password(), shopify_url(), 3)
	customers_cleaned_json = clean_json(new_customers_json, shopify_defined_subheaders_customers)
	orders_df = pd.json_normalize(customers_cleaned_json)
	cleaned_customers_df = clean_df(orders_df, shopify_defined_subheaders_customers)
	save_df_to_csv(cleaned_customers_df, path_gen('shopify', 'customers', 'clean', 'csv'))

def main_update_shopify_customer_report():
	#todo trying to load full data

	# Load existing customer report
	old_customers_df = load_csv(path_gen('shopify', 'customers', 'clean', 'csv'))

	# Get the most recent 'updated_at' from the old report
	most_recent_updated_at = get_shopify_most_recent_updated_at(old_customers_df)

	print(most_recent_updated_at)

	# Fetch updated customers
	if most_recent_updated_at:
		new_customers_json = get_shopify_customers_updated_after(shopify_api_key(), shopify_password(), shopify_url(), most_recent_updated_at)
	else:
		# Fetch all customers if there's no previous report
		new_customers_json = get_shopify_customers(shopify_api_key(), shopify_password(), shopify_url())

	# Clean new customer data
	new_customers_cleaned_json = clean_json(new_customers_json, shopify_defined_subheaders_customers)
	new_customers_df = pd.json_normalize(new_customers_cleaned_json)

	# Update the old customer report by merging and cleaning
	updated_customers_df = update_shopify_customers(old_customers_df, new_customers_df)
	updated_customers_df = clean_df(updated_customers_df, shopify_defined_subheaders_customers)

	# Save the updated report
	save_df_to_csv(updated_customers_df, path_gen('shopify', 'customers', 'clean', 'csv'))

def main_get_and_build_starshipit_report():
	unshipped_orders = get_unshipped_orders(starshipit_api_key(), starshipit_subscription_key(), 2, since, until)
	shipped_orders = get_shipped_orders(starshipit_api_key(), starshipit_subscription_key(), 2, since, until)
	unmanifested_shipments = get_unmanifested_shipments(starshipit_api_key(), starshipit_subscription_key(), 2, since, until)
	recently_printed_shipments = get_recently_printed_shipments(starshipit_api_key(), starshipit_subscription_key(), 2, since, until)
	df = combine_orders_to_df(unshipped_orders, shipped_orders, unmanifested_shipments, recently_printed_shipments)
	save_df_to_csv(df, path_gen('starshipit', 'orders', '', 'csv'))
	cleaned_df = clean_df(df, starshipit_defined_subheaders)
	save_df_to_csv(cleaned_df, path_gen('starshipit', 'orders', 'clean', 'csv'))

def get_and_build_google():
	credentials = get_credentials(google_credentials_path(), google_token_path())
	get_google_analytics_sheets(credentials, google_property_id(), since, until, path_gen('google'), google_defined_headers_dimensions, google_defined_headers_metrics)

def get_and_build_facebook():
	facebook_df = get_meta_insights(meta_access_token(),  meta_facebook_id(),  facebook_insights_headers, since, until, -1)
	save_df_to_csv(facebook_df, path_gen('facebook', 'data', '', 'csv'))
	clean_facebook_df = clean_df(facebook_df, ["end_time"]+facebook_insights_headers)
	split_insights_to_sheets(clean_facebook_df, facebook_insights_pages, path_gen('facebook'))

def get_and_build_instagram():
	insta_df = get_meta_insights(meta_access_token(), meta_insta_id(),instagram_insights_headers, since, until, -1)
	clean_insta_df = clean_df(insta_df,  ["end_time"]+instagram_insights_headers)
	save_df_to_csv(clean_insta_df, path_gen('instagram', 'data', 'clean', 'csv'))

def get_and_build_cin7():
	data = get_cin7_data(cin7_api_key())
	data = pd.json_normalize(data)
	cleaned_df = clean_df(data, cin7_defined_subheaders)
	save_df_to_csv(cleaned_df, path_gen('cin7', 'data', 'clean', 'csv'))

def excel_update():
	#todo keep a years worth of data
	#todo line up sheets by order number
	csv_files = [
		path_gen('shopify', 'orders', 'clean', 'csv'),
		path_gen('shopify', 'customers', 'clean', 'csv'),
		# path_gen('shopify', 'conversions', 'clean', 'csv'),
		path_gen('cin7', 'data', '', 'csv'),
		path_gen('starshipit', 'orders', 'clean', 'csv'),
		# path_gen('google', 'sessions', '', 'csv'),
		# path_gen('facebook', 'data', 'clean', 'csv'),
		path_gen('instagram', 'data', 'clean', 'csv')
	]
	csv_sheets_to_excel(csv_files, path_gen('compiled'))

def main():
	# main_get_and_build_starshipit_report()
	# main_get_and_build_shopify_order_report()
	# main_update_shopify_customer_report()
	# get_and_build_cin7()
	# get_and_build_instagram()

	# excel_update()

	# get_and_build_facebook()
	get_and_build_google()

if __name__ == '__main__':
	main()

# todo make a marketign data, Product data, Warehouse data sheet (email on the 27th)