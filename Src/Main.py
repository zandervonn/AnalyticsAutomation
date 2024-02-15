from shopifyautomation import *
from shopify_csv_handeling import *
from csvHelpers import *
from shopifyUiAutomation import *


shopify_api_key = access.shopify_api_key()
shopify_password = access.shopify_password()
shopify_url = access.shopify_url()

FOLDER_PATH = "gitignore\\"
# FOLDER_PATH = "C:\\Users\\Zander\\Desktop\\gel\\"
JSON_PATH = "orders.json"
CLEAN_JSON_PATH = "orders_clean.json"
ORDERS_PATH = "shopify_orders.csv"
ORDERS_CLEANED_PATH = "shopify_orders_clean.csv"
ORDERS_REPURCHASE_PATH = "shopify_orders_repurchase.csv"

shopify_defined_subheaders = [
	'order_number', 'updated_at', 'confirmation_number', 'contact_email',
	'total_line_items_price', 'discount_codes.code', 'discount_codes.amount',
	'current_subtotal_price', 'total_shipping_price_set.shop_money.amount', 'total_tip_received',
	'current_total_price', 'current_total_tax',
	'landing_site', 'name', 'note',  'payment_gateway_names', 'total_weight', 'customer.id',
	'customer.email', 'customer.first_name', 'customer.last_name', 'line_items.id',
	'line_items.name', 'line_items.price', 'fulfillments.id', 'fulfillments.created_at'
]

def main_get_and_build_report():
	existing_orders = load_json(FOLDER_PATH + JSON_PATH)
	last_update = get_most_recent_updated_at(existing_orders)
	new_orders_json = get_orders(shopify_api_key, shopify_password, shopify_url, 2)
	# new_orders_json = get_orders_updated_after(shopify_api_key, shopify_password, shopify_url, last_update)

	# Update existing orders with new orders
	updated_orders_json = update_orders(existing_orders, new_orders_json)
	sorted_orders_json = sort_orders_by_order_number(updated_orders_json)
	save_json(sorted_orders_json, FOLDER_PATH + JSON_PATH)

	# Load orders from JSON
	# orders_json = load_json(FOLDER_PATH + JSON_PATH)

	# Clean the JSON data
	orders_cleaned_json = clean_json(sorted_orders_json, shopify_defined_subheaders)
	save_json(orders_cleaned_json, FOLDER_PATH + CLEAN_JSON_PATH)

	# Convert the JSON data to a DataFrame
	orders_df = pd.json_normalize(orders_cleaned_json)
	# orders_df.to_csv(FOLDER_PATH + ORDERS_PATH)

	# Clean DataFrame
	cleaned_orders_df = clean_df(orders_df, shopify_defined_subheaders)
	save_df_to_csv(cleaned_orders_df, FOLDER_PATH + ORDERS_CLEANED_PATH)

def main():
	main_get_and_build_report()
	# get_ui_analytics()

if __name__ == '__main__':
	main()