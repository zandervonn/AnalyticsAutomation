import time
import requests

from Src.helpers.json_helpers import *

waitTime = 0.51

def get_starshipit_orders(url, api_key, subscription_key, status='', date_param_name=None, since_date=None, pages=None):
	headers = {
		'Content-Type': 'application/json',
		'StarShipIT-Api-Key': api_key,
		'Ocp-Apim-Subscription-Key': subscription_key
	}
	params = {
		'limit': 250,
		'page': 1
	}
	if since_date:
		params[date_param_name] = since_date

	all_orders = []
	total_pages = 1  # Initialize total_pages to enter the loop

	while params['page'] <= total_pages:
		request_time = time.time()  # Record the time at the start of the request
		print("Page: ", params['page'])
		response = requests.get(url, headers=headers, params=params)
		if response.status_code == 200:
			data = response.json()
			orders = data.get('orders', [])
			if not orders:
				break
			for order in orders:
				order['status'] = status
			all_orders.extend(orders)
			total_pages = data.get('total_pages', 0)
			if pages is not None and pages >= 0 and params['page'] >= pages:
				break
			params['page'] += 1

			# Calculate elapsed time and sleep if necessary
			elapsed_time = time.time() - request_time
			if elapsed_time < waitTime:
				time.sleep(waitTime - elapsed_time)

		else:
			print(f'Failed to get data: {response.status_code} - {response.text}')
			break

	print(f"Total orders retrieved: {len(all_orders)}")
	return all_orders


def get_unshipped_orders(api_key, subscription_key, pages=None, since_order_date=None):
	url = 'https://api.starshipit.com/api/orders/unshipped/'
	return get_starshipit_orders(url, api_key, subscription_key, 'unshipped', 'since_order_date', since_order_date, pages)

def get_shipped_orders(api_key, subscription_key, pages=None, since_last_updated=None):
	url = 'https://api.starshipit.com/api/orders/shipped/'
	return get_starshipit_orders(url, api_key, subscription_key, 'shipped', 'since_last_updated', since_last_updated, pages)

def get_unmanifested_shipments(api_key, subscription_key, pages=None, since_created_date=None):
	url = f'https://api.starshipit.com/api/orders/shipments/?status=unmanifested&since_created_date{since_created_date}'
	return get_starshipit_orders(url, api_key, subscription_key, '', '', since_created_date, pages)

def get_recently_printed_shipments(api_key, subscription_key, pages=None, since_created_date=None):
	url = f'https://api.starshipit.com/api/orders/shipments/?status=recently_printed&since_created_date{since_created_date}'
	return get_starshipit_orders(url, api_key, subscription_key, '', '', pages)

def get_all_starshipit_data(api_key, subscription_key, pages=None, since_date=None):
	unshipped_orders = get_unshipped_orders(api_key, subscription_key, pages, since_date)
	shipped_orders = get_shipped_orders(api_key, subscription_key, pages, since_date)
	shipped_orders = update_orders_with_tracking_details(api_key, subscription_key, shipped_orders)
	df = combine_orders_to_df(unshipped_orders, shipped_orders)
	return df

def get_tracking_details(api_key, subscription_key, tracking_number):
	url = f'https://api.starshipit.com/api/track?tracking_number={tracking_number}'
	headers = {
		'Content-Type': 'application/json',
		'StarShipIT-Api-Key': api_key,
		'Ocp-Apim-Subscription-Key': subscription_key
	}

	response = requests.get(url, headers=headers)
	if response.status_code == 200:
		return response.json()
	else:
		print(f'Failed to get tracking details for {tracking_number}: {response.status_code} - {response.text}')
		return None

def update_orders_with_tracking_details(api_key, subscription_key, orders):
	total = len(orders)
	i = 0
	for order in orders:
		request_time = time.time()
		tracking_number = order.get('tracking_number')
		if tracking_number:
			tracking_details = get_tracking_details(api_key, subscription_key, tracking_number)
			if tracking_details:
				order.update(tracking_details)
		i += 1
		# Calculate elapsed time and sleep if necessary
		elapsed_time = time.time() - request_time
		if elapsed_time < waitTime:
			time.sleep(waitTime - elapsed_time)

		print(f'Tracking: {i}/{total}')

	return orders

def combine_orders_to_df(*order_lists):
	dfs = []
	for order_list in order_lists:
		df = robust_json_to_df(order_list)
		dfs.append(df)
	combined_df = pd.concat(dfs, ignore_index=True)
	return combined_df

def robust_json_to_df(json_data):
	if not json_data:
		return pd.DataFrame()
	if isinstance(json_data, dict):
		json_data = [json_data]
	try:
		df = pd.json_normalize(json_data)
	except Exception as e:
		print(f"Error converting JSON to DataFrame: {e}")
		return pd.DataFrame()
	return df