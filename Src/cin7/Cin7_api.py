import time
from collections import defaultdict
from datetime import datetime, timedelta

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

def get_cin7_sales_data(api_key, start_date, end_date):
	base_url = 'https://api.cin7.com/api/v1/'
	endpoint = "SalesOrders"
	headers = {
		'Authorization': api_key,
	}

	all_data = []
	page = 1

	while True:
		url = f'{base_url}{endpoint}?where=createddate>=%27{start_date}Z%27 AND createddate<=%27{end_date}Z%27&fields=id,createddate,billingCompany,lineitems&page={page}&rows=250'
		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			data = response.json()
			all_data.extend(data)
			if len(data) < 250:
				break
			page += 1
			print("Sales Page", page)
			time.sleep(1)  # Delay to comply with rate limiting
		else:
			print(f'Error: {response.status_code}')
			return None

	return all_data

def get_cin7_purchase_orders(api_key):
	base_url = 'https://api.cin7.com/api/v1/'
	endpoint = "PurchaseOrders"
	headers = {
		'Authorization': api_key,
	}

	all_data = []
	page = 1

	while True:
		url = f'{base_url}{endpoint}?fields=id,createdDate,isApproved,reference,total,status,fullyReceivedDate&page={page}&rows=250'
		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			data = response.json()
			all_data.extend(data)
			if len(data) < 250:
				break
			page += 1
			print("Purchase Order Page", page)
			time.sleep(1)  # Delay to comply with rate limiting
		else:
			print(f'Error: {response.status_code}')
			return None

	return all_data

def get_cin7_production_jobs(api_key):
	base_url = 'https://api.cin7.com/api/v1/'
	endpoint = "ProductionJobs"
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
			print("Production Jobs Page", page)
			time.sleep(1)  # Delay to comply with rate limiting
		else:
			print(f'Error: {response.status_code}')
			return None

	return all_data

def filter_out_australia(sales_data):
	# Filter out entries where 'billingCustomer' equals 'Symet Australia Pty Ltd'
	filtered_data = [entry for entry in sales_data if entry.get('billingCompany') != 'Symet Australia Pty Ltd']
	return filtered_data

def get_open_purchase_orders(purchase_orders):
	# Filter purchase orders that are approved and not fully received
	open_orders = [
		order for order in purchase_orders
		if order.get('isApproved', False) == True and order.get('fullyReceivedDate') is None
	]

	# Calculate the sum of the 'total' column for the filtered purchase orders
	total = sum(float(order.get('total', 0)) for order in open_orders)

	return total

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

def aggregate_sales_by_category(sales_data):
	# Initialize a dictionary to hold the aggregated data
	aggregated_data = defaultdict(lambda: defaultdict(int))

	# Loop through the sales data and aggregate the quantities by date and category
	for record in sales_data:
		date = record['date']
		category = record.get('category', 'OTHER')  # Use 'OTHER' if 'category' key is missing
		quantity = record['quantity']
		aggregated_data[date][category] += quantity

	# Convert the aggregated data into a list of dictionaries for easier processing
	aggregated_list = []
	for date, categories in aggregated_data.items():
		row = {'Date': date}
		row.update(categories)
		aggregated_list.append(row)

	return aggregated_list

def aggregate_sales_by_product_id(sales_data, products):
	# Create a dictionary mapping product IDs to their names
	product_names = {product['id']: product['name'] for product in products}

	# Initialize a dictionary to hold the aggregated data
	aggregated_data = defaultdict(int)

	# Loop through the sales data and aggregate the quantities by product ID
	for record in sales_data:
		product_id = record['product_id']
		quantity = record['quantity']
		aggregated_data[product_id] += quantity

	# Convert the aggregated data into a list of dictionaries for easier processing
	aggregated_list = [{'Product Name': product_names.get(product_id, 'Unknown'), 'Total Sales': total_sales}
	                   for product_id, total_sales in aggregated_data.items()]

	# Sort the list by total sales in descending order
	aggregated_list.sort(key=lambda x: x['Total Sales'], reverse=True)

	# Extract the top performers where total sales > 10
	top_performers = [product for product in aggregated_list if product['Total Sales'] >= 10]

	# Find bottom performers (products with 0 sales, marked as 'Public', not 'Discontinued', not in category 'Packaging', and have stock on hand)
	bottom_performers = [{'Product Name': product['name'], 'Total Sales': 0}
	                     for product in products if product['id'] not in aggregated_data and
	                     product.get('status', '') == 'Public' and
	                     product.get('subCategory', '') != 'Discontinued' and
	                     product.get('category', '') != 'PACKAGING' and
	                     any(option.get('stockOnHand', 0) > 0 for option in product.get('productOptions', []))]

	# Calculate the maximum length to standardize DataFrame creation
	max_length = max(len(top_performers), len(bottom_performers))

	# Create a DataFrame with the top and bottom performers
	df = pd.DataFrame({
		'Top Product': [product['Product Name'] for product in top_performers] + [''] * (max_length - len(top_performers)),
		'Top Product Total': [product['Total Sales'] for product in top_performers] + [''] * (max_length - len(top_performers)),
		'Bottom Product': [product['Product Name'] for product in bottom_performers] + [''] * (max_length - len(bottom_performers)),
		'Bottom Product Total': [product['Total Sales'] for product in bottom_performers] + [''] * (max_length - len(bottom_performers))
	})

	return df

def calculate_inventory_values(products, purchases_nz, purchases_aus):
	total_retail_value = 0
	total_cost_value = 0
	total_unit_count = 0

	for product in products:
		for option in product.get('productOptions', []):
			# Extract relevant values from product option
			stock_on_hand = option.get('stockOnHand', 0) or 0
			retail_price = option.get('priceColumns', {}).get('retailNZD', 0) or 0
			cost_price = option.get('priceColumns', {}).get('costNZD', 0) or 0

			# Ignore negative stock on hand
			if stock_on_hand < 0:
				stock_on_hand = 0

			# Update totals
			total_retail_value += stock_on_hand * retail_price
			total_cost_value += stock_on_hand * cost_price
			total_unit_count += stock_on_hand

	open_purchases_nz = get_open_purchase_orders(purchases_nz)
	open_purchases_aus = get_open_purchase_orders(purchases_aus)
	total = open_purchases_nz - open_purchases_aus
	print(f"total: {open_purchases_nz} - {open_purchases_aus} = {total}")

	# Create a DataFrame with the totals
	df = pd.DataFrame({
		'SOH Retail Value': [f"${total_retail_value:,.2f}"],
		'SOH Stock Value': [f"${total_cost_value:,.2f}"],
		'SOH': [total_unit_count],
		'Open Purchase Orders': [total]
	})

	return df

def parse_aged_record(record):
	# Extract the completed date from the record level
	completed_date = record.get('completedDate')
	if completed_date:
		# Adjust timezone offset here if necessary
		completed_date = pd.to_datetime(completed_date, utc=True) + timedelta(hours=13)
		completed_date = completed_date.date()  # Convert to date format
	else:
		# Define default value for completedDate if it's None
		completed_date = datetime.now().date()  # or any other default date

	# Flatten the components within each product
	products = record.get('products', [])
	for product in products:
		components = product.get('components', [])
		for component in components:
			yield {
				'Date': completed_date,  # Use the completed date from record level
				'Ref': record.get('reference'),
				'Code': component.get('code'),
				'Product': component.get('name'),
				'Option1': component.get('option1'),
				'Option2': component.get('option2'),
				'Qty': component.get('standardQty'),
				'Branch': record.get('company'),  # Assuming default value
				'Value': component.get('unitCost'),
				'Days Old': '',  # Calculated later
			}

def calculate_aged_inventory(production_jobs):
	flattened_data = [component for record in production_jobs for component in parse_aged_record(record)]
	inventory_df = pd.DataFrame(flattened_data)

	# Assuming 'Date' is already in the correct format after parse_record
	current_date = datetime.now().date()
	inventory_df['Days Old'] = inventory_df['Date'].apply(lambda x: (current_date - x).days if pd.notnull(x) else 0)

	# Replace NaNs or NaTs with an empty string or a default value for 'Date'
	inventory_df['Date'] = inventory_df['Date'].fillna('')

	return inventory_df
