# graphql 200 points/second, 1000 total points
# rest 4 requests/second, 40 or 80 bucket size

import requests
import csv
import time
from Src import access

def get_limited_orders(page_limit):
	shopify_api_key = access.shopify_api_key()
	shopify_password = access.shopify_password()
	shopify_url = access.shopify_url()
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = "orders.json?limit=250&status=any"  # Max limit per request
	url = base_url + endpoint

	all_orders = []
	pages_fetched = 0
	urls_used = []  # List to keep track of all URLs used

	while url and pages_fetched < page_limit:
		response = requests.get(url, auth=(shopify_api_key, shopify_password))
		urls_used.append(url)  # Add the current URL to the list
		if response.status_code == 200:
			orders = response.json().get('orders', [])
			all_orders.extend(orders)
			pages_fetched += 1

			# Check if rate limit is approached, and wait if necessary
			rate_limit = response.headers.get('X-Shopify-Shop-Api-Call-Limit')
			if rate_limit:
				current, max_limit = map(int, rate_limit.split('/'))
				if current > max_limit * 0.8:  # If exceeding 80% of the rate limit
					time.sleep(10)  # Wait for 10 seconds before the next request

			# Extracting pagination 'page_info' from the 'Link' header
			link_header = response.headers.get('Link', None)
			next_page_info = None
			if link_header:
				links = link_header.split(',')
				for link in links:
					if 'rel="next"' in link:
						next_page_info = link.split("page_info=")[-1].split(">")[0]
						break

			# Construct next URL using base URL and next_page_info
			if next_page_info:
				url = f"{base_url}orders.json?limit=250&page_info={next_page_info}"
			else:
				url = None
		elif response.status_code == 429:  # Too Many Requests
			print("Rate limit exceeded, waiting...")
			time.sleep(10)  # Wait for 10 seconds before retrying
			# Optionally, you could adjust the waiting time based on the Retry-After header if present
		else:
			print(f"Failed to retrieve orders, status code: {response.status_code}")
			break

	print(f"Total orders retrieved: {len(all_orders)}")
	print("URLs used:")
	for url in urls_used:
		print(url)

	return all_orders

def write_orders_to_csv(orders, filename='orders.csv'):
	# Define the header of the CSV file
	headers = ['Order ID', 'Order Date', 'Total Price']

	# Open the CSV file for writing
	with open(filename, mode='w', newline='', encoding='utf-8') as file:
		writer = csv.writer(file)

		# Write the header
		writer.writerow(headers)

		# Write the order data
		for order in orders:
			order_id = order.get('id')
			order_date = order.get('created_at')
			total_price = order.get('total_price')
			writer.writerow([order_id, order_date, total_price])

def saveOrdersToCsvDynamicHeaders(all_orders, path='shopify_orders.csv'):
	# Ensure all_orders is a list for consistency
	if isinstance(all_orders, dict):
		all_orders = [all_orders]  # Wrap in a list if it's a single order

	if not all_orders:
		print("No orders to save.")
		return

	# Assuming all orders have the same keys, use the keys of the first order as headers
	headers = list(all_orders[0].keys())

	with open(path, 'w', newline='', encoding='utf-8') as file:
		writer = csv.writer(file)
		writer.writerow(headers)  # Write the headers derived from order keys

		for order in all_orders:
			# Write row values in the order of the headers
			row = [order.get(header, 'N/A') for header in headers]
			writer.writerow(row)

	print(f"Orders saved to {path}")