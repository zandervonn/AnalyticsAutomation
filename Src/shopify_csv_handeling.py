import pandas as pd
import matplotlib.pyplot as plt
import requests

from Src.gitignore import access

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

def saveOrdersToCsvDynamicHeaders(all_orders, path):
	# Ensure all_orders is a list for consistency
	if isinstance(all_orders, dict):
		all_orders = [all_orders]  # Wrap in a list if it's a single order

	if not all_orders:
		print("No orders to save.")
		return

	# Assuming all orders have the same keys, use the keys of the first order as headers
	headers = list(all_orders[0].keys())

	with open(path, 'w', newline='', encoding='utf-8') as file:
		writer = csv.writer(file)
		writer.writerow(headers)  # Write the headers derived from order keys

		for order in all_orders:
			# Write row values in the order of the headers
			row = [order.get(header, 'N/A') for header in headers]
			writer.writerow(row)

	print(f"Orders saved to {path}")



def retrieve_shopify_report(report):
	shopify_api_key = access.shopify_api_key()
	shopify_password = access.shopify_password()
	shopify_url = access.shopify_url()
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = f"reports/{report}.json"
	url = base_url + endpoint
	headers = {"Content-Type": "application/json"}
	query = "SHOW total_sales BY order_id FROM sales SINCE -1m UNTIL today ORDER BY total_sales"
	data = {
		"query": query
	}

	response = requests.get(url)

	if response.status_code == 200:
		report_data = response.json()  # Extract JSON data from the response
		print(json.dumps(report_data, indent=4))  # Now you are serializing the JSON data, not the Response object
	else:
		print(f"Failed to retrieve report: {response.status_code}")
		print(response.text)


import json
import csv

def json_to_reduced_csv(json_file_path, csv_file_path):
	# Open and load the JSON data
	with open(json_file_path, 'r', encoding='utf-8') as json_file:
		json_data = json.load(json_file)

	with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
		writer = csv.writer(file)
		# Write the header row
		writer.writerow(['Order ID', 'Date', 'Customer', 'Channel', 'total', 'Payment Status', 'Fulfillment status','Items', 'Delivery status', 'Delivery method', 'tags'])

		# Ensure json_data is a list
		if isinstance(json_data, dict):  # If it's a single order, wrap it in a list
			json_data = [json_data]

		# Iterate through each order in the JSON data
		for order in json_data:
			# Safely extract billing_address and customer details
			billing_address = order.get('billing_address') or {}
			customer = order.get('customer') or {}

			writer.writerow([
				order.get('id', ''),
				billing_address.get('name', ''),
				customer.get('id', ''),
				order.get('created_at', '')
			])

def analyze_repurchase_trends(csv_file_path):

	# Sample DataFrame
	df = pd.read_csv(csv_file_path)

	# Ensure 'Date' is in datetime format
	df['Date'] = pd.to_datetime(df['Date'], utc=True)

	# Sort by CustomerID and Date
	df.sort_values(by=['Customer ID', 'Date'], inplace=True)

	# Calculate the difference in days between consecutive purchases for each customer
	df['DaysBetweenPurchases'] = df.groupby('Customer ID')['Date'].diff().dt.days

	# Filter out first purchase for each customer since it doesn't have a preceding purchase
	df_filtered = df.dropna(subset=['DaysBetweenPurchases'])

	# Calculate average days between purchases per period (e.g., monthly)
	df_filtered['YearMonth'] = df_filtered['Date'].dt.to_period('M')
	average_time_between_purchases = df_filtered.groupby('YearMonth')['DaysBetweenPurchases'].mean()

	# Plotting
	average_time_between_purchases.plot(kind='line', figsize=(10, 6))
	plt.title('Average Time Between Repurchases Over Time')
	plt.xlabel('Time Period')
	plt.ylabel('Average Days Between Purchases')
	plt.grid(True)
	plt.show()