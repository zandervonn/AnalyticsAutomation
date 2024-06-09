from Src.cin7.UI.cin7_ui_automation import cin7_get_ui_reports
from Src.helpers.clean_csv_helpers import clean_df, clean_dfs
from Src.starshipit.UI.starshipit_ui_automation import *
from Src.starshipit.starshipit_api import *
from Src.cin7.Cin7_api import *
from Src.google.google_automation import *
from Src.helpers.file_helpers import *
from Src.helpers.time_helpers import *
from Src.meta.meta_automation import *
from Src.shopify.shopify_automation import *
from Src.shopify.UI.shopify_ui_automation import *
from Src.access import *

access.secrets = load_properties(find_path_upwards(r'config/secrets.txt'))

since, until = get_dates("sunday", "weeks", 1)
testing = True


def build_report_shopify_ui(branch):
	print("Getting Shopify UI")
	_since, _until = convert_dates_to_offsets(since, until)
	shopify_ui_dfs = get_ui_analytics(get_header_list('shopify_ui'), _since, _until, branch)
	shopify_ui_dfs = combine_shopify_reports(shopify_ui_dfs)
	shopify_ui_dfs = clean_shopify_ui_dfs(shopify_ui_dfs, )
	save_df_to_excel(shopify_ui_dfs, path_gen(branch, 'shopify', 'data', 'xlsx'))


def build_report_starshipit_api(branch):
	print("Getting Starshipit API")
	df = get_all_starshipit_data(starshipit_api_key(), starshipit_subscription_key(), -1, since)
	cleaned_df = clean_df(df, get_header_list('starshipit'))
	save_df_to_csv(cleaned_df, path_gen(branch, 'starshipit', 'orders', 'csv'), True)


def build_report_starshipit_ui(branch, testing=False):
	print("Getting Starshipit UI")
	_since, _until = get_dates("sunday", "months", 1)
	df = starshipit_get_ui_report(_since, _until, branch, testing)
	cleaned_df = clean_df(df, get_header_list("starshipit_ui"))
	processed_df = process_starshipit_ui_report(cleaned_df, branch)

	open_orders = get_open_orders_count(shopify_api_key(), shopify_password(), shopify_url())
	processed_df = add_open_orders_to_starshipit(processed_df, open_orders)

	save_df_to_excel(processed_df, path_gen(branch, 'starshipit', 'warehouse_report', 'xlsx'))


def build_report_google():
	print("Getting Google")
	credentials = get_credentials(google_credentials_path(), google_token_path())
	google_dfs = get_google_analytics_sheets(credentials, google_property_id(), since, until,
	                                         get_header_list('google_dimensions'), get_header_list('google_metrics'))
	google_dfs = clean_dfs(google_dfs, get_header_list('google_dimensions') + get_header_list('google_metrics'))
	google_dfs = clean_google_dfs(google_dfs)

	today = datetime.now().strftime("%Y-%m-%d")
	save_df_to_excel(google_dfs, todays_output_folder()+"\Google New Zealand " + today + ".xlsx")


def build_report_facebook():
	print("Getting Facebook")
	_since, _until = get_dates("sunday", "weeks", 2)  # get 2 weeks of data to show change over the week
	facebook_df = get_meta_insights(meta_access_token(), meta_facebook_id(), get_header_list('facebook'), _since,
	                                _until)
	clean_facebook_df = clean_df(facebook_df, ["end_time"] + get_header_list('facebook'))
	split_facebook_df = split_insights_to_sheets(clean_facebook_df, get_header_list('facebook_pages'))
	save_df_to_excel(split_facebook_df, path_gen(NZ, 'facebook', 'data', 'xlsx'))

	meta_files = [
		path_gen(NZ, 'facebook', 'data', 'xlsx'),
		path_gen(NZ, 'facebook_posts', 'data', 'csv'),
		path_gen(NZ, 'facebook_videos', 'data', 'csv'),
		path_gen(NZ, 'instagram', 'data', 'csv'),
		path_gen(NZ, 'instagram', 'videos', 'csv'),
		path_gen(NZ, 'instagram', 'images', 'csv'),
	]

	today = datetime.now().strftime("%Y-%m-%d")
	path = todays_output_folder() + "\Facebook New Zealand " + today + ".xlsx"
	files_to_excel(meta_files, path)


def build_report_facebook_posts():
	print("Getting Facebook posts")
	_since, _until = get_dates("sunday", "weeks", 2)  # get 2 weeks of data to show change over the week
	facebook_df = get_facebook_posts_and_insights(meta_access_token(), meta_facebook_id(),
	                                              get_header_list('facebook_posts'), _since, _until)
	facebook_df = clean_df(facebook_df, get_header_list('facebook_posts'))
	facebook_df = clean_facebook_post_df(facebook_df)
	save_df_to_csv(facebook_df, path_gen(NZ, 'facebook_posts', 'data', 'csv'), True)


def build_report_facebook_videos():
	print("Getting Facebook videos")
	_since, _until = get_dates("sunday", "weeks", 2)  # get 2 weeks of data to show change over the week
	facebook_df = get_facebook_video_insights(meta_access_token(), meta_facebook_id(), _since, _until)
	facebook_df = clean_df(facebook_df, get_header_list('facebook_videos'))
	facebook_df = clean_facebook_post_df(facebook_df)
	save_df_to_csv(facebook_df, path_gen(NZ, 'facebook_videos', 'data', 'csv'), True)


def build_report_instagram_videos():
	print("Getting Instagram videos")
	_since, _until = get_dates("sunday", "weeks", 2)  # get 2 weeks of data to show change over the week
	insta_df = get_insta_video_insights(meta_access_token(), meta_insta_id(), _since, _until)
	insta_df = clean_insta_video_df(insta_df)
	save_df_to_csv(insta_df, path_gen(NZ, 'instagram', 'videos', 'csv'), True)


def build_report_instagram_images():
	print("Getting Instagram images")
	_since, _until = get_dates("sunday", "weeks", 2)  # get 2 weeks of data to show change over the week
	insta_df = get_insta_image_insights(meta_access_token(), meta_insta_id(), _since, _until)
	insta_df = clean_insta_image_df(insta_df)
	save_df_to_csv(insta_df, path_gen(NZ, 'instagram', 'images', 'csv'), True)


def build_report_instagram():
	print("Getting Instagram")
	_since, _until = get_dates("sunday", "weeks", 2)  # get 2 weeks of data to show change over the week
	insta_df = get_meta_insights(meta_access_token(), meta_insta_id(), get_header_list('instagram'), _since, _until)
	clean_insta_df = clean_df(insta_df, ["end_time"] + get_header_list('instagram'))
	save_df_to_csv(clean_insta_df, path_gen(NZ, 'instagram', 'data', 'csv'), True)


def build_report_cin7_ui(branch):
	print("Getting Cin7 Aged Report")
	cin7_ui_reports = cin7_get_ui_reports(branch)
	save_df_to_excel(cin7_ui_reports, path_gen(branch, 'cin7', 'data', 'xlsx'))


def build_report_cin7(branch):
	if branch == access.AUS:
		API_key = cin7_api_key_AUS()
	else:  # branch == access.NZ:
		API_key = cin7_api_key_NZ()

	print("Getting Cin7 Products")
	products = get_all_products(API_key)

	print("Getting Cin7 Sales")
	sales_data = get_cin7_sales_data(API_key, since, until)
	if branch == access.NZ:
		sales_data = filter_out_australia(sales_data)

	print("Getting Cin7 Sales by Product Categories")
	matched_data = match_sales_with_products(sales_data, products)
	category_data_df = aggregate_sales_by_category(matched_data)
	category_data_df = clean_df(category_data_df, ['Date'] + get_header_list('cin7_categories'))
	save_df_to_csv(category_data_df, path_gen(branch, 'cin7', 'Sale_by_Categories', 'csv'), True)

	print("Getting Cin7 Top Selling Products")
	top_selling = aggregate_sales_by_product_id(matched_data, products)
	save_df_to_csv(top_selling, path_gen(branch, 'cin7', 'Top_Selling', 'csv'), True)

	# print("Getting Cin7 Purchase Orders")
	# purchases_nz = get_cin7_purchase_orders(cin7_api_key_NZ())
	# purchases_aus = get_cin7_purchase_orders(cin7_api_key_AUS())

	# print("Getting Cin7 Stock Values")
	# stock_values = calculate_inventory_values(branch, products, purchases_nz, purchases_aus)
	# stock_values = clean_numeric_columns(stock_values)
	# save_df_to_csv(stock_values, path_gen(branch, 'cin7', 'stock_values', 'csv'), True)


# todo keep a years worth of data
def build_previous_report(branch):
	previous_marketing = get_latest_marketing_file(final_output_path(), "New Zealand", since)
	save_df_to_csv(previous_marketing, path_gen(branch, 'previous', 'marketing', 'csv'), True)


def main_NZ():
	branch = NZ

	build_report_cin7_ui(branch)  # needs 2fa
	# build_report_starshipit_ui(branch, testing=testing)
	# build_report_shopify_ui(branch)
	# build_previous_report(branch)
	# build_report_cin7(branch)
	# build_report_instagram()
	# build_report_instagram_images()
	# build_report_instagram_videos()
	# build_report_facebook_videos()
	# build_report_facebook_posts()
	#
	# build_report_facebook()
	# build_report_google()

	update_template_files(template_folder_path_NZ(), output_folder_path() + "/" + branch, todays_output_folder())


def main_AUS():
	branch = AUS

	# build_report_cin7_ui(branch)  # needs 2fa
	# build_report_starshipit_ui(branch, testing=testing)
	# build_report_shopify_ui(branch)
	# build_previous_report(branch)
	# build_report_cin7(branch)

	update_template_files(template_folder_path_AUS(), output_folder_path() + "/" + branch, todays_output_folder())


def main():
	main_NZ()
	# main_AUS()


if __name__ == '__main__':
	main()
