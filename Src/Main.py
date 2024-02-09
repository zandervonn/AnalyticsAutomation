from shopifyautomation import *

def main():

	# download_data()
	# test_connection()
	# print(get_limited_orders())
	write_orders_to_csv(get_limited_orders(3))
	# print(get_most_recent_order())
	# saveOrdersToCsvDynamicHeaders(all_orders,'shopify_orders.csv')
	# print(get_shop_details())


if __name__ == '__main__':
	main()