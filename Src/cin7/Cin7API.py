import time
from collections import defaultdict

import pandas as pd
import requests



def get_all_products(api_key):
	base_url = 'https://api.cin7.com/api/v1/'
	endpoint = "Products"
	headers = {
		'Authorization': api_key,
	}

	all_data = []
	page = 1

	while True:
		url = f'{base_url}{endpoint}?page={page}&rows=250'
		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			data = response.json()
			all_data.extend(data)
			if len(data) < 250:
				break
			page += 1
			print("Page ", page)
			time.sleep(1)  # Delay to comply with rate limiting
		else:
			print(f'Error: {response.status_code}')
			return None

	return all_data

def get_cin7_sales_data(api_key, start_date, end_date, rows_per_call=250):
	base_url = 'https://api.cin7.com/api/v1/'
	endpoint = "SalesOrders"
	headers = {
		'Authorization': api_key,
	}

	all_data = []
	page = 1

	while True:
		url = f'{base_url}{endpoint}?where=createddate>=%27{start_date}Z%27 AND createddate<=%27{end_date}Z%27&fields=id,createddate,lineitems&page={page}&rows={rows_per_call}'
		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			data = response.json()
			all_data.extend(data)
			if len(data) < rows_per_call:
				break
			page += 1
			print("Sales Page", page)
			time.sleep(1)  # Delay to comply with rate limiting
		else:
			print(f'Error: {response.status_code}')
			return None

	return all_data

def match_sales_with_products(sales_data, products):
	# Create a dictionary mapping product IDs to their categories
	product_categories = {product['id']: product['category'].strip() for product in products}

	matched_data = []
	for order in sales_data:
		order_date = order['createdDate'][:10]  # Extract the date part from the datetime string
		for item in order.get('lineItems', []):
			product_id = item['productId']
			category = product_categories.get(product_id, 'Unknown').strip()  # Default to 'Unknown' if category not found
			quantity = item.get('qty', 0)
			matched_data.append({
				'date': order_date,
				'product_id': product_id,
				'product_name': item.get('name', ''),
				'category': category,
				'quantity': quantity,
			})
	return matched_data

def aggregate_sales_data(sales_data):
	# Initialize a dictionary to hold the aggregated data
	aggregated_data = defaultdict(lambda: defaultdict(int))

	# Loop through the sales data and aggregate the quantities by date and category
	for record in sales_data:
		# print("Current record:", record)  # Debug print
		date = record['date']
		category = record.get('category', 'OTHER')  # Use 'Unknown' if 'category' key is missing
		quantity = record['quantity']
		aggregated_data[date][category] += quantity

	# Convert the aggregated data into a list of dictionaries for easier processing
	aggregated_list = []
	for date, categories in aggregated_data.items():
		row = {'Date': date}
		row.update(categories)
		aggregated_list.append(row)

	return aggregated_list