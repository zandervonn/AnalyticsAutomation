# graphql 200 points/second, 1000 total points
# rest 4 requests/second, 40 or 80 bucket size

import requests
import csv
import time
from Src import access
import json

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

def save_orders_to_json(orders, filename='orders.json'):
	with open(filename, 'w', encoding='utf-8') as f:
		json.dump(orders, f, ensure_ascii=False, indent=4)
	print(f"Orders saved to {filename}")

def load_orders_from_json(orders_path):
	with open(orders_path, 'r', encoding='utf-8') as f:
		orders = json.load(f)
	return orders

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

def flatten_dict(d, parent_key='', sep='_'):
	items = []
	for k, v in d.items():
		new_key = f"{parent_key}{sep}{k}" if parent_key else k
		if isinstance(v, dict):
			items.extend(flatten_dict(v, new_key, sep=sep).items())
		elif isinstance(v, list):
			if v and isinstance(v[0], dict):
				for i, item in enumerate(v):
					items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
			else:
				items.append((new_key, json.dumps(v)))
		else:
			items.append((new_key, v))
	return dict(items)


def save_orders_to_csv_dynamic_headers(all_orders, path='shopify_orders.csv'):
	if isinstance(all_orders, dict):
		all_orders = [all_orders]

	if not all_orders:
		print("No orders to save.")
		return

	# Flatten all orders
	flattened_orders = [flatten_dict(order) for order in all_orders]

	# Collect all unique headers from the flattened orders
	headers = set()
	for order in flattened_orders:
		headers.update(order.keys())
	headers = list(headers)

	with open(path, 'w', newline='', encoding='utf-8') as file:
		writer = csv.DictWriter(file, fieldnames=headers)
		writer.writeheader()
		for order in flattened_orders:
			writer.writerow(order)

	print(f"Orders saved to {path}")