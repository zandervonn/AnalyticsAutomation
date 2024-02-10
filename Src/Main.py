from shopifyautomation import *

def main():
	saveOrdersToCsvDynamicHeaders(get_limited_orders(3))
	#getReq()


if __name__ == '__main__':
	main()