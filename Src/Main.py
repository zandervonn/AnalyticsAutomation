from shopifyautomation import *
from shopify_csv_handeling import *
from csvHelpers import *


FOLDER_PATH = "gitignore\\"
# FOLDER_PATH = "C:\\Users\\Zander\\Desktop\\gel\\"
JSON_PATH = "orders.json"
ORDERS_PATH = "shopify_orders.csv"
ORDERS_CLEANED_PATH = "shopify_orders_clean.csv"
ORDERS_REPURCHASE_PATH = "shopify_orders_repurchase.csv"

def main_get_orders():
	# orders = get_orders(3)
	orders=load_orders_from_json(FOLDER_PATH+JSON_PATH)
	save_orders_to_json(orders, FOLDER_PATH+JSON_PATH)

	shopify_defined_headers = [
		'checkout_id', 'confirmation_number', 'contact_email', 'created_at',
		'current_subtotal_price', 'current_total_discounts', 'current_total_price',
		'current_total_tax', 'discount_codes', 'landing_site', 'name', 'note',
		'order_number', 'payment_gateway_names', 'total_discounts', 'total_tip_received',
		'total_weight', 'customer', 'fulfillments', 'line_items'
	]

	saveOrdersToCsvDynamicHeadersTrimmed(orders, FOLDER_PATH+ORDERS_PATH, shopify_defined_headers)

	cleanCsv(FOLDER_PATH+ORDERS_PATH, FOLDER_PATH+ORDERS_CLEANED_PATH)

def main_repurchase_trends():
	# json_to_reduced_csv(FOLDER_PATH+JSON_PATH, FOLDER_PATH+ORDERS_REPURCHASE_PATH)
	analyze_repurchase_trends(FOLDER_PATH+ORDERS_REPURCHASE_PATH)

def main_api_report():
	# build_shopify_report()
	retrieve_shopify_report("2788983086")

def main():
	main_get_orders()

if __name__ == '__main__':
	main()