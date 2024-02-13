from shopifyautomation import *
from csvHelpers import *

def main():
	orders = get_orders(3)
	save_orders_to_json(orders, 'gitignore\\orders.json')
	# orders = load_orders_from_json('gitignore/orders.json')

	saveOrdersToCsvDynamicHeaders(orders, "gitignore\\shopify_orders.csv")

	cleanCsv("gitignore\\shopify_orders.csv", "gitignore\\shopify_orders_clean.csv")


if __name__ == '__main__':
	main()