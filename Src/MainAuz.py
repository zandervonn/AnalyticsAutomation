from Src.cin7.UI.cin7_ui_automation import cin7_get_ui_aged_report
from Src.helpers.clean_csv_helpers import clean_df
from Src.starshipit.UI.starshipit_ui_automation import *
from Src.cin7.Cin7_api import *
from Src.helpers.file_helpers import *
from Src.helpers.time_helpers import *
from Src.shopify.shopify_automation import *
from Src.shopify.UI.shopify_ui_automation import *
from Src.access import *

since, until = get_dates("sunday", "weeks", 1)
branch = AUS

def build_report_shopify_ui():
	_since, _until = convert_dates_to_offsets(since, until)
	shopify_ui_dfs = get_ui_analytics(get_header_list('shopify_ui'), _since, _until, branch)
	shopify_ui_dfs = combine_shopify_reports(shopify_ui_dfs)
	shopify_ui_dfs = clean_shopify_ui_dfs(shopify_ui_dfs, )
	save_df_to_excel(shopify_ui_dfs, path_gen('shopify', 'data', 'xlsx', branch=branch))

def build_report_starshipit_ui(testing=False):
	print("Getting Starshipit UI")
	_since, _until = get_dates("sunday", "months", 1)
	df = starshipit_get_ui_report(_since, _until, branch, testing)
	cleaned_df = clean_df(df, get_header_list("starshipit_ui"))
	processed_df = process_starshipit_ui_report_AUS(cleaned_df)

	open_orders = get_open_orders_count(shopify_api_key(), shopify_password(), shopify_url())
	processed_df = add_open_orders_to_starshipit(processed_df, open_orders)

	save_df_to_excel(processed_df, path_gen('starshipit', 'warehouse_report', 'xlsx', branch=branch))

def build_report_cin7_ui():
	aged_report = cin7_get_ui_aged_report(branch)
	save_df_to_csv(aged_report, path_gen('cin7', 'aged', 'csv', branch=branch), True)

def build_report_cin7():
	print("Getting Cin7 Products")
	products = get_all_products(cin7_api_key_AUS())

	print("Getting Cin7 Sales")
	sales_data = get_cin7_sales_data(cin7_api_key_AUS(), since, until)

	print("Getting Cin7 Purchase Orders")
	purchases_nz = get_cin7_purchase_orders(cin7_api_key_NZ())
	purchases_aus = get_cin7_purchase_orders(cin7_api_key_AUS())

	print("Getting Cin7 Sales by Product Categories")
	matched_data = match_sales_with_products(sales_data, products)
	category_data_df = aggregate_sales_by_category(matched_data)
	category_data_df = clean_df(category_data_df, ['Date'] + get_header_list('cin7_categories'))
	save_df_to_csv(category_data_df, path_gen('cin7', 'Sale_by_Categories', 'csv', branch=branch), True)

	print("Getting Cin7 Top Selling Products")
	top_selling = aggregate_sales_by_product_id(matched_data, products)
	save_df_to_csv(top_selling, path_gen('cin7', 'Top_Selling', 'csv', branch=branch), True)

	print("Getting Cin7 Stock Values")
	stock_values = calculate_inventory_values(products, purchases_aus, purchases_nz)
	stock_values = clean_numeric_columns(stock_values)
	save_df_to_csv(stock_values, path_gen('cin7', 'stock_values', 'csv', branch=branch), True)

#todo keep a years worth of data
def excel_update():
	csv_files = [
		path_gen('shopify', 'data', 'xlsx', branch=branch),
		path_gen('starshipit', 'orders', 'csv', branch=branch),
	]
	files_to_excel(csv_files, path_gen('compiled', branch=branch))

	csv_files = [
		path_gen('cin7', 'Sale_by_Categories', 'csv', branch=branch),
		path_gen('cin7', 'Top_Selling', 'csv', branch=branch),
		path_gen('cin7', 'stock_values', 'csv', branch=branch),
	]
	files_to_excel(csv_files, path_gen('cin7', branch=branch))

def main():
	# build_report_cin7_ui() #needs 2fa
	# build_report_shopify_ui()
	# build_report_starshipit_ui(testing=True)
	# build_report_cin7()
	#
	excel_update() #todo remove need for this, pull from raw
	update_template_files(template_folder_path_AUS(), output_folder_path() + "\\" + branch, final_output_path())

if __name__ == '__main__':
	main()
