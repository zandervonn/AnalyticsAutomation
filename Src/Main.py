from shopifyautomation import *

def main():
	write_orders_to_csv(get_limited_orders(3))
	#getReq()


if __name__ == '__main__':
	main()