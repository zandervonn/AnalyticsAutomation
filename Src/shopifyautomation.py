# graphql 200 points/second, 1000 total points
# rest 4 requests/second, 40 or 80 bucket size

import requests
import time
from Src.gitignore import access
import json

# -1 is all orders
# otherwise page limit is * 250 orders
def get_orders(page_limit):
	shopify_api_key = access.shopify_api_key()
	shopify_password = access.shopify_password()
	shopify_url = access.shopify_url()
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = "orders.json?limit=250&status=any"  # Max limit per request
	url = base_url + endpoint

	all_orders = []
	pages_fetched = 0

	while url and (pages_fetched < page_limit or page_limit == -1):
		n = pages_fetched * 250
		print(f"rows fetched = {n}")

		response = requests.get(url, auth=(shopify_api_key, shopify_password))
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

	return all_orders

def save_orders_to_json(orders, filename='orders.json'):
	with open(filename, 'w', encoding='utf-8') as f:
		json.dump(orders, f, ensure_ascii=False, indent=4)
	print(f"Orders saved to {filename}")

def load_orders_from_json(orders_path):
	with open(orders_path, 'r', encoding='utf-8') as f:
		orders = json.load(f)
	return orders

def build_shopify_report():
	shopify_api_key = access.shopify_api_key()
	shopify_password = access.shopify_password()
	shopify_url = access.shopify_url()
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = "reports.json"

	url = base_url + endpoint
	headers = {"Content-Type": "application/json"}
	data = {
		"report": {
			"category": "Sales",
			"name": "My API Report",
			"shopify_ql": "SHOW total_sales BY order_id FROM sales SINCE -1m UNTIL today ORDER BY total_sales"
		}
	}

	response = requests.post(url, json=data, headers=headers)
	print(response.json())