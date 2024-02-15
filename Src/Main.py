from shopifyautomation import *
from shopify_csv_handeling import *
from csvHelpers import *


FOLDER_PATH = "gitignore\\"
# FOLDER_PATH = "C:\\Users\\Zander\\Desktop\\gel\\"
JSON_PATH = "orders.json"
CLEAN_JSON_PATH = "orders_clean.json"
ORDERS_PATH = "shopify_orders.csv"
ORDERS_CLEANED_PATH = "shopify_orders_clean.csv"
ORDERS_REPURCHASE_PATH = "shopify_orders_repurchase.csv"

shopify_defined_subheaders = [
	'checkout_id', 'confirmation_number', 'contact_email', 'created_at',
	'total_line_items_price', 'discount_codes.code', 'discount_codes.amount',
	'current_subtotal_price', 'total_shipping_price_set.shop_money.amount', 'total_tip_received',
	'current_total_price', 'current_total_tax',
	'landing_site', 'name', 'note', 'order_number', 'payment_gateway_names', 'total_weight', 'customer.id',
	'customer.email', 'customer.first_name', 'customer.last_name', 'line_items.id',
	'line_items.name', 'line_items.price', 'fulfillments.id', 'fulfillments.created_at'
]

def main_get_and_build_report():
	# Load orders from JSON
	orders_json = load_json(FOLDER_PATH + JSON_PATH)

	# Clean the JSON data
	orders_cleaned_json = clean_json(orders_json, shopify_defined_subheaders)
	save_json(orders_cleaned_json, FOLDER_PATH + CLEAN_JSON_PATH)

	# Convert the JSON data to a DataFrame
	orders_df = pd.json_normalize(orders_cleaned_json)
	# orders_df.to_csv(FOLDER_PATH + ORDERS_PATH)

	# Clean DataFrame
	cleaned_orders_df = clean_df(orders_df, shopify_defined_subheaders)
	save_df_to_csv(cleaned_orders_df, FOLDER_PATH + ORDERS_CLEANED_PATH)


def main():
	main_get_and_build_report()


if __name__ == '__main__':
	main()