import time
import requests

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

def get_starshipit_orders(starshipit_url, starshipit_api_key, starshipit_subscription_key, pages=-1):
	headers = {
		'Content-Type': 'application/json',
		'StarShipIT-Api-Key': f'{starshipit_api_key}',
		'Ocp-Apim-Subscription-Key': f'{starshipit_subscription_key}'
	}
	params = {
		'limit': 50
		# 'since_created_date': "2024-01-29T22:46:58.7155685Z"
	}

	return get_starshipit_paginated_data(starshipit_url, headers, params, pages)

def get_starshipit_paginated_data(url, headers, params, max_pages=None):
	rate_limit_delay = 0.2  # API limit is 5 per second
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