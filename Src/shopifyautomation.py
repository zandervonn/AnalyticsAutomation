# graphql 200 points/second, 1000 total points
# rest 4 requests/second, 40 or 80 bucket size

import requests
import csv
from Src import access
from urllib.parse import urlparse, urlunparse

def get_limited_orders(page_limit):
	base_url = f"https://{access.shopify_api_key()}:{access.shopify_password()}@{access.shopify_url()}/admin/api/2024-01/"
	endpoint = "orders.json?limit=2"  # Adjust the limit as needed for testing
	url = base_url + endpoint

	all_orders = []
	pages_fetched = 0

	while url and pages_fetched < page_limit:
		response = requests.get(url)
		print(url)
		if response.status_code == 200:
			orders = response.json().get('orders', [])
			all_orders.extend(orders)
			pages_fetched += 1

			# Extracting pagination links from the 'Link' header
			link_header = response.headers.get('Link', None)
			next_link = None
			if link_header:
				links = link_header.split(',')
				for link in links:
					if 'rel="next"' in link:
						next_url = link.split(';')[0].strip('<> ')
						# Reconstruct the URL with authentication
						parsed_url = urlparse(next_url)
						next_link = urlunparse((parsed_url.scheme, f"{access.shopify_api_key()}:{access.shopify_password()}@{parsed_url.netloc}", parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment))
						break

			url = next_link
		else:
			print(f"Failed to retrieve orders, status code: {response.status_code}")
			break

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