from Src.StarshipitAPI import *
from Src.helpers.fileHelpers import *
from Src.meta.metaAutomation import *
from Src.shopify.shopifyautomation import *
from Src.shopify.shopify_csv_handeling import *
from Src.helpers.csvHelpers import *
from Src.shopify.shopifyUiAutomation import *
from config import *

shopify_api_key = access.shopify_api_key()
shopify_password = access.shopify_password()
shopify_url = access.shopify_url()

starshipit_api_key = access.starshipit_api_key()
starshipit_password = access.starshipit_subscription_key()
starshipit_url = access.starshipit_url()

def main_get_and_build_shopify_order_report():
	# existing_orders = load_json(FOLDER_PATH + JSON_PATH)
	# last_update = get_most_recent_updated_at(existing_orders)
	# new_orders_json = get_orders(shopify_api_key, shopify_password, shopify_url, 2)
	new_orders_json = get_shopify_orders_updated_after(shopify_api_key, shopify_password, shopify_url, "2024-02-19T09:00:00+1300")

	# Update existing orders with new orders
	# updated_orders_json = update_orders(existing_orders, new_orders_json)
	sorted_orders_json = sort_shopify_orders_by_order_number(new_orders_json)
	save_json(sorted_orders_json, path_gen('shopify', 'order', 'clean', 'json'))

	# Load orders from JSON
	# orders_json = load_json(FOLDER_PATH + JSON_PATH)

	# Clean the JSON data
	orders_cleaned_json = clean_json(sorted_orders_json, shopify_defined_subheaders_orders)
	save_json(orders_cleaned_json, path_gen('shopify', 'order', 'clean', 'json'))

	# Convert the JSON data to a DataFrame
	orders_df = pd.json_normalize(orders_cleaned_json)
	# orders_df.to_csv(FOLDER_PATH + ORDERS_PATH)

	# Clean DataFrame
	cleaned_orders_df = clean_df(orders_df, shopify_defined_subheaders_orders)
	cleaned_orders_df = shopify_clean_df(cleaned_orders_df)
	save_df_to_csv(cleaned_orders_df, path_gen('shopify', 'orders', 'clean', 'csv'))

def main_get_and_build_shopify_customer_report():
	new_orders_json = get_shopify_customers(shopify_api_key, shopify_password, shopify_url)
	save_json(new_orders_json, path_gen('shopify', 'customers', '', 'json'))

	# Clean the JSON data
	orders_cleaned_json = clean_json(new_orders_json, shopify_defined_subheaders_customers)
	save_json(orders_cleaned_json, path_gen('shopify', 'customers', 'clean', 'json'))

	# Convert the JSON data to a DataFrame
	orders_df = pd.json_normalize(orders_cleaned_json)

	# Clean DataFrame
	cleaned_orders_df = clean_df(orders_df, shopify_defined_subheaders_customers)
	# cleaned_orders_df = shopify_clean_df(cleaned_orders_df)
	save_df_to_csv(cleaned_orders_df, path_gen('shopify', 'customers', 'clean', 'csv'))

def excel_update():
	csv_files = [path_gen('shopify', 'orders', 'clean', 'csv'), path_gen('shopify', 'customers', 'clean', 'csv'), path_gen('shopify', 'conversions', 'clean', 'csv')]  # List of your CSV files
	excel_file = access.FOLDER_PATH + 'compiled_data.xlsx'  # Desired Excel file name
	csv_sheets_to_excel(csv_files, excel_file)

def main_get_and_build_starshipit_report():
	unshipped_orders = get_unshipped_orders(starshipit_api_key, starshipit_password, 2)
	shipped_orders = get_shipped_orders(starshipit_api_key, starshipit_password, 2)
	unmanifested_shipments = get_unmanifested_shipments(starshipit_api_key, starshipit_password, 2)
	recently_printed_shipments = get_recently_printed_shipments(starshipit_api_key, starshipit_password, 2)

	df = combine_orders_to_df(unshipped_orders, shipped_orders, unmanifested_shipments, recently_printed_shipments)

	save_df_to_csv(df, path_gen('starshipit', 'orders', '', 'csv'))

	cleaned_df = clean_df(df, starshipit_defined_subheaders)
	save_df_to_csv(cleaned_df, path_gen('starshipit', 'orders', 'clean', 'csv'))

def main():
	# main_get_and_build_starshipit_report()
	# main_get_and_build_shopify_report()
	# main_get_and_build_shopify_customer_report()
	get_meta_page_info(access.meta_access_token(), access.meta_id(), 1)

if __name__ == '__main__':
	main()