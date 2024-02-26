from Src.StarshipitAPI import *
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

def main_get_and_build_shopify_order_report():
	since, _ = get_dates("today", "weeks", 1)
	new_orders_json = get_shopify_orders_updated_after(shopify_api_key(), shopify_password(), shopify_url(), since)
	#sorted_orders_json = sort_shopify_orders_by_order_number(new_orders_json)
	orders_cleaned_json = clean_json(new_orders_json, shopify_defined_subheaders_orders)
	orders_df = pd.json_normalize(orders_cleaned_json)
	cleaned_orders_df = clean_df(orders_df, shopify_defined_subheaders_orders)
	cleaned_orders_df = shopify_clean_df(cleaned_orders_df)
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

def main_get_and_build_starshipit_report():
	since, until = get_dates("today", "weeks", 1)
	unshipped_orders = get_unshipped_orders(starshipit_api_key(), starshipit_subscription_key(), 2, since, until)
	shipped_orders = get_shipped_orders(starshipit_api_key(), starshipit_subscription_key(), 2, since, until)
	unmanifested_shipments = get_unmanifested_shipments(starshipit_api_key(), starshipit_subscription_key(), 2, since, until)
	recently_printed_shipments = get_recently_printed_shipments(starshipit_api_key(), starshipit_subscription_key(), 2, since, until)
	df = combine_orders_to_df(unshipped_orders, shipped_orders, unmanifested_shipments, recently_printed_shipments)

	cleaned_df = clean_df(df, starshipit_defined_subheaders)
	save_df_to_csv(cleaned_df, path_gen('starshipit', 'orders', 'clean', 'csv'))

def get_and_build_google():
	since, until = get_dates("today", "weeks", 1)
	credentials = get_credentials(google_credentials_path())
	response = get_google_analytics(credentials, google_property_id(), google_defined_headers_dimensions, google_defined_headers_metrics, since, until)
	save_df_to_csv(response, path_gen('google', 'sessions', '', 'csv'))

def get_and_build_facebook():
	since, until = get_dates("today", "weeks", 1)
	facebook_df = get_meta_insights(meta_access_token(),  meta_facebook_id(), facebook_insights_headers, since, until, -1)
	save_df_to_csv(facebook_df, path_gen('facebook', 'data', '', 'csv'))
	clean_facebook_df = clean_df(facebook_df, facebook_insights_headers)
	save_df_to_csv(clean_facebook_df, path_gen('facebook', 'data', 'clean', 'csv'))

def get_and_build_instagram():
	since, until = get_dates("today", "weeks", 1)
	insta_df = get_meta_insights(meta_access_token(), meta_insta_id(), instagram_insights_headers, since, until, -1)
	clean_insta_df = clean_df(insta_df, instagram_insights_headers)
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
		path_gen('google', 'sessions', '', 'csv'),
		path_gen('facebook', 'data', '', 'csv')
	]
	excel_file = FOLDER_PATH + 'compiled_data.xlsx'  # Desired Excel file name
	csv_sheets_to_excel(csv_files, excel_file)

def main():

	# main_get_and_build_starshipit_report()
	# main_get_and_build_shopify_order_report()
	# main_get_and_build_shopify_customer_report()
	# get_and_build_cin7()
	# get_and_build_instagram()
	# get_and_build_facebook()
	get_and_build_google()

	excel_update()

if __name__ == '__main__':
	main()

#todo make seperate sheets for raw data and calcualtons?