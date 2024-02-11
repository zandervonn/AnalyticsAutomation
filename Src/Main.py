from shopifyautomation import *
from csvHelpers import *

def main():
	# saveOrdersToCsvDynamicHeaders(get_limited_orders(3))
	cleanCsv("C:\\Users\\Zander\\IdeaProjects\\Automation-Gel\\Src\\shopify_orders.csv", "C:\\Users\\Zander\\IdeaProjects\\Automation-Gel\\Src\\shopify_orders_clean.csv")


if __name__ == '__main__':
	main()