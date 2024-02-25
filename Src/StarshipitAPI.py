import json
import time
import requests

from Src.helpers.jsonHelpers import *

def get_orders_after_date(orders, date):
	"""
	Filter orders to get those created after a given date.

	:param orders: List of orders.
	:param date: String representing the date in the format 'YYYY-MM-DD'.
	:return: List of orders created after the given date.
	"""
	from datetime import datetime

	date_threshold = datetime.strptime(date, '%Y-%m-%d')
	filtered_orders = [order for order in orders if datetime.strptime(order['order_date'][:10], '%Y-%m-%d') > date_threshold]
	return filtered_orders

def get_starshipit_orders(starshipit_url, starshipit_api_key, starshipit_subscription_key, pages=-1, order_type='', status=None, since_order_date=None, since_last_updated=None):
	headers = {
		'Content-Type': 'application/json',
		'StarShipIT-Api-Key': starshipit_api_key,
		'Ocp-Apim-Subscription-Key': starshipit_subscription_key
	}
	params = {
		'limit': 250,
	}
	if status:
		params['status'] = status
	if since_order_date:
		params['since_order_date'] = since_order_date
	if since_last_updated:
		params['since_last_updated'] = since_last_updated

	orders = get_starshipit_paginated_data(starshipit_url, headers, params, pages)
	for order in orders:
		order['order_type'] = order_type  # Append order type to each order
	return orders

def combine_orders_to_df(*order_lists):
	dfs = []
	for order_list in order_lists:
		df = robust_json_to_df(order_list)
		dfs.append(df)

	combined_df = pd.concat(dfs, ignore_index=True)
	return combined_df

def robust_json_to_df(json_data):
	# Check if the JSON data is empty or None
	if not json_data:
		return pd.DataFrame()

	# Ensure json_data is a list of dictionaries
	if isinstance(json_data, dict):
		json_data = [json_data]

	# Normalize the JSON data into a flat table
	try:
		df = pd.json_normalize(json_data)
	except Exception as e:
		print(f"Error converting JSON to DataFrame: {e}")
		return pd.DataFrame()

	return df

# Now update each of the specific order retrieval functions to accept the date parameters:
def get_unshipped_orders(api_key, subscription_key, pages=-1, since_order_date=None, since_last_updated=None):
	url = 'https://api.starshipit.com/api/orders/unshipped/'
	return get_starshipit_orders(url, api_key, subscription_key, pages, 'Unshipped', None, since_order_date, since_last_updated)

def get_shipped_orders(api_key, subscription_key, pages=-1, since_order_date=None, since_last_updated=None):
	url = 'https://api.starshipit.com/api/orders/shipped/'
	return get_starshipit_orders(url, api_key, subscription_key, pages, 'Shipped', None, since_order_date, since_last_updated)

def get_unmanifested_shipments(api_key, subscription_key, pages=-1, since_order_date=None, since_last_updated=None):
	url = 'https://api.starshipit.com/api/orders/shipments/'
	return get_starshipit_orders(url, api_key, subscription_key, pages, 'Unmanifested', 'unmanifested', since_order_date, since_last_updated)

def get_recently_printed_shipments(api_key, subscription_key, pages=-1, since_order_date=None, since_last_updated=None):
	url = 'https://api.starshipit.com/api/orders/shipments/'
	return get_starshipit_orders(url, api_key, subscription_key, pages, 'Recently Printed', 'recently_printed', since_order_date, since_last_updated)

def get_starshipit_paginated_data(url, headers, params, max_pages=None):
	rate_limit_delay = 1  # API limit is 2 per second
	all_data = []
	page = 1

	while True:

		if max_pages != -1 and page > max_pages:
			break  # Stop fetching if the maximum number of pages is reached

		print(f"fetching page: {page}")

		params['page'] = page
		response = requests.get(url, headers=headers, params=params)

		# print(response.headers)
		print(response)

		if response.status_code == 200:
			data = response.json()
			page_data = data.get('orders', [])
			if not page_data:
				break  # No more data to fetch
			all_data.extend(page_data)
			page += 1

			time.sleep(rate_limit_delay)  # Wait to respect the rate limit
		else:
			print(f'Failed to get data: {response.status_code} - {response.text}')
			break

	print(f"Total orders retrieved: {len(all_data)}")

	return all_data