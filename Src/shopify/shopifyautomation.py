import time

import pandas as pd
import requests
from gitignore import access
from datetime import datetime
from dateutil import tz


def fetch_pages(base_url, endpoint, type, page_limit=-1):
	url = base_url + endpoint
	all_data = []
	pages_fetched = 0

	while url and (pages_fetched < page_limit or page_limit == -1):
		response = requests.get(url)
		if pages_fetched == 0:
			print(response)
		else:
			print(f"Rows fetched= {pages_fetched * 250}")
		if response.status_code == 200:
			data = response.json().get(type, [])
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
				url = f"{base_url}{type}.json?limit=250&page_info={next_page_info}"
			else:
				url = None
		elif response.status_code == 429:  # Too Many Requests
			print("Rate limit exceeded, waiting...")
			time.sleep(10)  # Wait for 10 seconds before retrying
		else:
			print(f"Failed to retrieve data, status code: {response.status_code}")
			break

	print(f"Total lines retrieved: {len(all_data)}")

	return all_data

def get_shopify_orders(shopify_api_key, shopify_password, shopify_url, page_limit=-1):
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = "orders.json?limit=250&status=any"
	return fetch_pages(base_url, endpoint, 'orders', page_limit)

def get_shopify_customers(shopify_api_key, shopify_password, shopify_url, page_limit=-1):
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = "customers.json?limit=250"
	return fetch_pages(base_url, endpoint, 'customers', page_limit)

def get_shopify_orders_updated_after(shopify_api_key, shopify_password, shopify_url, updated_at_min, page_limit=-1):
	updated_at_min_utc = convert_to_utc(updated_at_min)
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = f"orders.json?limit=250&status=any&created_at_min={updated_at_min_utc}"
	return fetch_pages(base_url, endpoint, 'orders', page_limit)

def get_shopify_most_recent_updated_at(orders_json):
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

def get_shopify_customers_updated_after(shopify_api_key, shopify_password, shopify_url, updated_at_min, page_limit=-1):
	"""Fetches Shopify customers updated after a specified timestamp"""
	updated_at_min_utc = convert_to_utc(updated_at_min)
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = f"customers.json?limit=250&updated_at_min={updated_at_min_utc}"
	return fetch_pages(base_url, endpoint, 'customers', page_limit)

def update_shopify_customers(existing_customers_df, new_customers_df):
	"""Updates an existing DataFrame of Shopify customers with new customer data."""
	# Convert DataFrames to dictionaries for easier updates
	existing_customers_dict = existing_customers_df.set_index('id').to_dict('index')
	new_customers_dict = new_customers_df.set_index('id').to_dict('index')

	# Update or add entries
	existing_customers_dict.update(new_customers_dict)

	# Convert back to DataFrame, reset index, and return
	updated_df = pd.DataFrame.from_dict(existing_customers_dict, orient='index').reset_index()
	updated_df.rename(columns={'index': 'id'}, inplace=True)
	return updated_df

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



def update_shopify_orders(existing_orders, new_orders):
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

def sort_shopify_orders_by_order_number(orders):
	return sorted(orders, key=lambda order: int(order['order_number']), reverse=True)

def convert_to_utc(time_str, timezone_str="Pacific/Auckland"):
	# Set the default format for date string and adjust if time is included
	time_format = "%Y-%m-%d" if 'T' not in time_str else "%Y-%m-%dT%H:%M:%S"

	# Parse the time string into a datetime object
	local_time = datetime.strptime(time_str, time_format)

	# Set the timezone to the specified timezone
	local_timezone = tz.gettz(timezone_str)
	local_time = local_time.replace(tzinfo=local_timezone)

	# Convert the time to UTC
	utc_time = local_time.astimezone(tz.tzutc())

	# Format the UTC time as a string, add 'T00:00:00' if only date is provided
	utc_time_str = utc_time.strftime("%Y-%m-%dT%H:%M:%S%z" if 'T' in time_str else "%Y-%m-%dT00:00:00%z")

	return utc_time_str
