import time

import pandas as pd
import requests
from Src import access
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
	# Convert datetime object to string
	updated_at_min_str = updated_at_min.strftime("%Y-%m-%dT%H:%M:%S%z")

	updated_at_min_utc = convert_to_shopify_format_utc(updated_at_min_str, "%Y-%m-%dT%H:%M:%S%z")
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = f"orders.json?limit=250&status=any&processed_at_min={updated_at_min_utc}"
	return fetch_pages(base_url, endpoint, 'orders', page_limit)

def get_shopify_customers_updated_after(shopify_api_key, shopify_password, shopify_url, updated_at_min, page_limit=-1):
	# Convert datetime object to string
	updated_at_min_str = updated_at_min.strftime("%Y-%m-%dT%H:%M:%S%z")

	updated_at_min_utc = convert_to_shopify_format_utc(updated_at_min_str, "%Y-%m-%dT%H:%M:%S%z")
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = f"customers.json?limit=250&updated_at_min={updated_at_min_utc}"
	return fetch_pages(base_url, endpoint, 'customers', page_limit)


def get_shopify_most_recent_updated_at(df, input_format):
	# Extract 'updated_at' values and convert them to datetime objects
	updated_at_dates = [
		datetime.strptime(order['updated_at'], input_format)
		for index, order in df.iterrows()
		if 'updated_at' in order
	]

	# Find the most recent date
	if updated_at_dates:
		most_recent_date = max(updated_at_dates)
		return most_recent_date.strftime(input_format)
	else:
		return None

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


def update_dataframe(old_df, new_df, id_column):
	# Set the index to the id column for easy merging
	old_df.set_index(id_column, inplace=True)
	new_df.set_index(id_column, inplace=True)

	# Update the old DataFrame with the new DataFrame
	updated_df = old_df.combine_first(new_df)

	# Reset the index to bring the id column back as a regular column
	updated_df.reset_index(inplace=True)

	# Sort the DataFrame based on the id column to maintain the original order
	updated_df.sort_values(by=id_column, inplace=True)

	return updated_df


def sort_shopify_orders_by_order_number(orders):
	return sorted(orders, key=lambda order: int(order['order_number']), reverse=True)

def convert_to_shopify_format_utc(time_str, timezone_str="Pacific/Auckland"):
	# Define the allowed formats
	allowed_formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S%z', '%Y-%m-%d %H:%M:%S']

	# Check if the input matches one of the allowed formats
	for fmt in allowed_formats:
		try:
			local_time = datetime.strptime(time_str, fmt)
			break
		except ValueError:
			continue
	else:
		raise ValueError(f"Time string '{time_str}' does not match the allowed formats.")

	# Set the timezone to the specified timezone if it's not already set
	if local_time.tzinfo is None:
		local_timezone = tz.gettz(timezone_str)
		local_time = local_time.replace(tzinfo=local_timezone)

	# Convert the time to UTC
	utc_time = local_time.astimezone(tz.tzutc())

	# Format the UTC time in the Shopify format
	shopify_format = "%Y-%m-%dT%H:%M:%SZ"
	shopify_time_str = utc_time.strftime(shopify_format)

	print("shopify time: ", shopify_time_str)

	return shopify_time_str

def get_open_orders_count(shopify_api_key, shopify_password, shopify_url):
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = "orders/count.json?status=open"  # Query for count of open orders
	url = base_url + endpoint

	response = requests.get(url)
	if response.status_code == 200:
		count_data = response.json()
		open_orders_count = count_data.get('count', 0)  # Default to 0 if not found
		return open_orders_count
	else:
		print(f"Failed to retrieve data, status code: {response.status_code}")
		return -1