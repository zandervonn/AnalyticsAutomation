# graphql 200 points/second, 1000 total points
# rest 4 requests/second, 40 or 80 bucket size

import requests
import time
from Src.gitignore import access
import json
from datetime import datetime
from dateutil import tz

# -1 is all orders
# otherwise page limit is * 250 orders
def fetch_pages(base_url, endpoint, page_limit):
	url = base_url + endpoint
	all_data = []
	pages_fetched = 0

	while url and (pages_fetched < page_limit or page_limit == -1):
		response = requests.get(url)
		if pages_fetched == 0:
			print(response)
		else:
			print(f"pages fetched= {pages_fetched}")
		if response.status_code == 200:
			data = response.json().get('orders', [])
			all_data.extend(data)
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
		else:
			print(f"Failed to retrieve data, status code: {response.status_code}")
			break

	print(f"Total orders retrieved: {len(all_data)}")

	return all_data

def get_orders(shopify_api_key, shopify_password, shopify_url, page_limit=-1):
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = "orders.json?limit=250&status=any"
	return fetch_pages(base_url, endpoint, page_limit)

def get_orders_updated_after(shopify_api_key, shopify_password, shopify_url, updated_at_min, page_limit=-1):
	updated_at_min_utc = convert_to_utc(updated_at_min)
	print("Getting orders after: " + updated_at_min)
	print("Getting orders after utc: " + updated_at_min_utc)
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = f"orders.json?limit=250&status=any&created_at_min={updated_at_min_utc}"
	return fetch_pages(base_url, endpoint, page_limit)

def save_json(orders, filename='orders.json'):
	with open(filename, 'w', encoding='utf-8') as f:
		json.dump(orders, f, ensure_ascii=False, indent=4)
	print(f"Orders saved to {filename}")

def load_json(orders_path):
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

def get_most_recent_updated_at(orders_json):
	# Extract 'updated_at' values and convert them to datetime objects
	updated_at_dates = [
		datetime.strptime(order['updated_at'], "%Y-%m-%dT%H:%M:%S%z")
		for order in orders_json
		if 'updated_at' in order
	]

	# Find the most recent date
	if updated_at_dates:
		most_recent_date = max(updated_at_dates)
		return most_recent_date.strftime("%Y-%m-%dT%H:%M:%S%z")
	else:
		return None

def update_orders(existing_orders, new_orders):
	# Create a dictionary to hold the existing orders, using the order ID as the key
	existing_orders_dict = {order['id']: order for order in existing_orders}

	# List to hold the new orders that are not in the existing orders
	new_orders_to_prepend = []

	# Update existing orders or add new orders to the prepend list
	for order in new_orders:
		if order['id'] in existing_orders_dict:
			existing_orders_dict[order['id']] = order
		else:
			new_orders_to_prepend.append(order)

	# Prepend the new orders to the existing orders list
	updated_orders_list = new_orders_to_prepend + list(existing_orders_dict.values())

	return updated_orders_list

def sort_orders_by_order_number(orders):
	return sorted(orders, key=lambda order: int(order['order_number']), reverse=True)

def convert_to_utc(time_str):
	timezone_str = "Pacific/Auckland"
	# Parse the time string into a datetime object
	local_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S%z")

	# Set the timezone to the specified timezone
	local_timezone = tz.gettz(timezone_str)
	local_time = local_time.replace(tzinfo=local_timezone)

	# Convert the time to UTC
	utc_time = local_time.astimezone(tz.tzutc())

	# Format the UTC time as a string
	utc_time_str = utc_time.strftime("%Y-%m-%dT%H:%M:%S%z")

	return utc_time_str
