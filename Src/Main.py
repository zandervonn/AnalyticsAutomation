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

since, until = get_dates("today", "weeks", 1)

def main_get_and_build_all_shopify_order_report():
	print("Getting Shopify orders")
	new_orders_json = get_shopify_orders(shopify_api_key(), shopify_password(), shopify_url())
	new_orders_json = clean_json(new_orders_json, get_header_list('shopify_orders'))
	orders_df = pd.json_normalize(new_orders_json)
	cleaned_orders_df = shopify_orders_clean_df(orders_df)
	cleaned_orders_df = clean_df(cleaned_orders_df, get_header_list('shopify_orders'))
	save_df_to_csv(cleaned_orders_df, path_gen('shopify', 'orders', 'csv'))

def main_get_and_build_all_shopify_customer_report():
	#todo get just the number of current users
	print("Getting Shopify customers")
	new_customers_json = get_shopify_customers(shopify_api_key(), shopify_password(), shopify_url())
	customers_cleaned_json = clean_json(new_customers_json, get_header_list('shopify_customers'))
	orders_df = pd.json_normalize(customers_cleaned_json)
	cleaned_customers_df = clean_df(orders_df, get_header_list('shopify_customers'))
	cleaned_customers_df = sort_by_date_column(cleaned_customers_df, ['updated_at'])
	save_df_to_csv(cleaned_customers_df, path_gen('shopify', 'customers', 'csv'))

def main_update_shopify_customer_report():
	print("Getting Shopify customers")
	shopify_customer_path = path_gen('shopify', 'customers', 'csv')

	# Get new report
	new_customers_json = get_shopify_customers_updated_after(shopify_api_key(), shopify_password(), shopify_url(), get_last_run_timestamp())
	new_customers_df = pd.json_normalize(new_customers_json)
	cleaned_new_customers_df = clean_df(new_customers_df, get_header_list('shopify_customers'))

	# Load the old customer report
	old_customers_df = load_csv(shopify_customer_path)

	# Update the old customer report by merging and cleaning
	updated_customers_df = update_dataframe(old_customers_df, cleaned_new_customers_df, 'id')
	updated_customers_df = clean_df(updated_customers_df, get_header_list('shopify_customers'))
	updated_customers_df = sort_by_date_column(updated_customers_df, 'updated_at')

	# Save the updated report
	save_df_to_csv(updated_customers_df, shopify_customer_path)

def main_update_shopify_order_report():
	print("Getting Shopify orders")
	shopify_order_path = path_gen('shopify', 'orders', 'csv')

	# get new order data
	new_orders_json = get_shopify_orders_updated_after(shopify_api_key(), shopify_password(), shopify_url(), get_last_run_timestamp())
	new_orders_df = pd.json_normalize(new_orders_json)
	cleaned_new_orders_df = shopify_orders_clean_df(new_orders_df)
	cleaned_new_orders_df = clean_df(cleaned_new_orders_df, get_header_list('shopify_orders'))

	# Update the old order report by merging and cleaning
	old_orders_df = load_csv(shopify_order_path)
	updated_orders_df = update_dataframe(old_orders_df, cleaned_new_orders_df, 'order_number')
	updated_orders_df = clean_df(updated_orders_df, get_header_list('shopify_orders'))
	updated_orders_df = sort_by_value_column(updated_orders_df, 'order_number')

	# Save the updated report
	save_df_to_csv(updated_orders_df, shopify_order_path)

def main_get_and_build_starshipit_report():
	print("Getting Starshipit")
	df = get_all_starshipit_data(starshipit_api_key(), starshipit_subscription_key(), -1, since)
	# save_df_to_csv(df, path_gen('starshipit', 'orders', 'csv'))
	cleaned_df = clean_df(df, get_header_list('starshipit'))
	save_df_to_csv(cleaned_df, path_gen('starshipit', 'orders', 'csv'))

def get_and_build_google():
	print("Getting Google")
	credentials = get_credentials(google_credentials_path(), google_token_path())
	google_dfs = get_google_analytics_sheets(credentials, google_property_id(), since, until, get_header_list('google_dimensions'), get_header_list('google_metrics'))
	google_dfs = clean_dfs(google_dfs, get_header_list('google_dimensions')+get_header_list('google_metrics'))
	google_dfs = clean_google_dfs(google_dfs)
	save_df_to_excel(google_dfs, path_gen('google'))

def get_and_build_facebook():
	print("Getting Facebook")
	facebook_df = get_meta_insights(meta_access_token(),  meta_facebook_id(),  get_header_list('facebook'), since, until)
	save_df_to_csv(facebook_df, path_gen('facebook', 'data', 'csv'))
	clean_facebook_df = clean_df(facebook_df, ["end_time"]+get_header_list('facebook'))
	split_facebook_df = split_insights_to_sheets(clean_facebook_df, get_header_list('facebook_pages'))
	save_df_to_excel(split_facebook_df, path_gen('facebook'))

def get_and_build_facebook_posts():
	print("Getting Facebook")
	facebook_df = get_posts_and_insights(meta_access_token(),  meta_facebook_id(), get_header_list('facebook_posts'), since, until)
	facebook_df = clean_df(facebook_df, ["created_time", "message"]+get_header_list('facebook_posts'))
	save_df_to_csv(facebook_df, path_gen('facebook_posts', 'data', 'csv'))

#todo complete
def get_and_build_instagram_posts():
	print("Getting Facebook")
	facebook_df = get_posts_and_insights(meta_access_token(),  meta_insta_id(), since, until)
	save_df_to_csv(facebook_df, path_gen('facebook_posts', 'data', 'csv'))
	clean_facebook_df = clean_df(facebook_df, ["end_time"]+get_header_list('facebook'))
	split_facebook_df = split_insights_to_sheets(clean_facebook_df, get_header_list('facebook_pages'))
	save_df_to_excel(split_facebook_df, path_gen('facebook_posts'))

def get_and_build_instagram():
	print("Getting Instagram")
	insta_df = get_meta_insights(meta_access_token(), meta_insta_id(), get_header_list('instagram'), since, until)
	clean_insta_df = clean_df(insta_df,  ["end_time"]+get_header_list('instagram'))
	save_df_to_csv(clean_insta_df, path_gen('instagram', 'data', 'csv'))

def get_and_build_cin7():
	print("Getting Cin7")
	data = get_cin7_data(cin7_api_key())
	data = pd.json_normalize(data)
	cleaned_df = clean_df(data, get_header_list('cin7'))
	save_df_to_csv(cleaned_df, path_gen('cin7', 'data', 'csv'))

#todo keep a years worth of data
def excel_update():
	csv_files = [
		path_gen('shopify', 'orders', 'csv'),
		path_gen('shopify', 'customers', 'csv'),
		path_gen('cin7', 'data', 'csv'),
		path_gen('starshipit', 'orders', 'csv'),
		path_gen('instagram', 'data', 'csv'),
		path_gen('facebook_posts', 'data', 'csv'),
	]
	csv_sheets_to_excel(csv_files, path_gen('compiled'))

def main():
	# main_update_shopify_customer_report()
	# main_update_shopify_order_report()
	#
	# main_get_and_build_starshipit_report()
	# get_and_build_cin7()
	# get_and_build_instagram()
	# get_and_build_facebook_posts()
	#
	# excel_update()
	#
	# get_and_build_google()
	# get_and_build_facebook()

	update_files(find_path_upwards('gitignore/output'), find_path_upwards('gitignore/custom'))

	# set_last_run_timestamp()

if __name__ == '__main__':
	main()