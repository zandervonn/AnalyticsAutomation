from shopifyautomation import *
from csvHelpers import *

def main():
	# orders = get_limited_orders(3)
	# save_orders_to_json(orders, 'orders.json')

	orders = load_orders_from_json('orders.json')

	save_orders_to_csv_dynamic_headers(orders)

	cleanCsv("C:\\Users\\Zander\\IdeaProjects\\Automation-Gel\\Src\\shopify_orders.csv", "C:\\Users\\Zander\\IdeaProjects\\Automation-Gel\\Src\\shopify_orders_clean.csv")


if __name__ == '__main__':
	main()