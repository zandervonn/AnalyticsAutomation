# graphql 200 points/second, 1000 total points
# rest 4 requests/second, 40 or 80 bucket size


import requests
import csv
import errno
import gzip
import json
import logging
import shutil
import tempfile
from time import sleep
from pathlib import Path
from Src import access
from access import *
from typing import Type

import shopify
from shopify import ShopifyResource, session

version = '2024-01'  # API version

# Setting up the request headers
headers = {
	"Content-Type": "application/json",
	"X-Shopify-Access-Token": access.shopify_password()
}

# print(headers)

# # Configure logging at the start of your script
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_most_recent_order():
	# Fetch the most recent order by sorting orders by created_at date in descending order and limiting to 1
	url = f"https://{access.shopify_api_key()}:{access.shopify_password()}@{access.shopify_url()}/admin/api/{version}/shop.json"
	response = requests.get(url, headers=headers)
	print(response)
	if response.status_code == 200:
		data = response.json()
		if data['orders']:
			return data['orders'][0]  # Return the most recent order
		else:
			return "No orders found."
	else:
		return f"Failed to retrieve the most recent order, status code: {response.status_code}"


def get_shop_details():
	url = f"https://{access.shopify_api_key()}:{access.shopify_password()}@{access.shopify_url()}/admin/api/{version}/shop.json"
	response = requests.get(url, headers=headers)
	if response.status_code == 200:
		return response.json()  # Successfully fetched shop details
	else:
		return f"Failed to retrieve shop details, status code: {response.status_code}"

def get_test_order():
	url = f"https://{access.shopify_api_key()}:{access.shopify_password()}@{access.shopify_url()}"

	# endpoint = "/admin/api/2024-01/orders/5638484230446.json?fields=id,line_items,name,total_price"
	endpoint = "/admin/api/2024-01/orders.json?limit=2"

	url = url+endpoint

	response = requests.get(url, headers=headers)
	if response.status_code == 200:
		return response.json()  # Successfully fetched shop details
	else:
		return f"Failed to retrieve shop details, status code: {response.status_code}"

def get_limited_orders(page_limit):
	base_url = f"https://{access.shopify_api_key()}:{access.shopify_password()}@{access.shopify_url()}"
	endpoint = "/admin/api/2024-01/orders.json?limit=2"  # Adjust the limit as needed for testing
	url = base_url + endpoint

	all_orders = []
	pages_fetched = 0

	while url and pages_fetched < page_limit:
		response = requests.get(url)
		print(url)
		if response.status_code == 200:
			orders = response.json().get('orders', [])
			all_orders.extend(orders)
			pages_fetched += 1

			# Extracting pagination links from the 'Link' header
			link_header = response.headers.get('Link', None)
			next_link = None
			if link_header:
				links = link_header.split(',')
				for link in links:
					if 'rel="next"' in link:
						next_link = link.split(';')[0].strip('<> ')
						break

			url = next_link
		else:
			print(f"Failed to retrieve orders, status code: {response.status_code}")
			break

	return all_orders

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


def test_connection():
	# shop_url = "https://{api_key}:{password}@{shopurl}/admin/".format(api_key=access.shopify_api_key(),
	#                                                                  password=access.shopify_password(),
	#                                                                  shopurl=access.shopify_url())
	shop_url = f"https://{access.shopify_api_key()}:{access.shopify_password()}@{access.shopify_url()}/admin/api/{version}/shop.json"

	orders = shopify.Order.find(since_id=0, status='any', limit=2)
	for order in orders:
		print("found order")
	while orders.has_next_page():
		orders = orders.next_page()
		for order in orders:
			print("found order page")

	shopify.ShopifyResource.set_site(shop_url)

	orders = shopify.Order.find()
	#orders = shopify.Product.find()
	if orders:
		most_recent_order = orders[0]
		print("Most Recent Order ID:", most_recent_order.id)
		# You can access other properties of the order as needed
		# e.g., print("Order Status:", most_recent_order.status)
	else:
		print("No orders found.")

	# shopify.ShopifyResource.clear_session()

def download_data():
	"""Creates a ShopifyApiClient and downloads the data"""
	logger = logging.basicConfig(level=logging.INFO,
	                             format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	shop_url = "https://{api_key}:{password}@{shopurl}/admin".format(api_key=access.shopify_api_key(),
	                                                                 password=access.shopify_password(),
	                                                                 shopurl=access.shopify_url())
	shopify.ShopifyResource.set_site(shop_url)
	download_data_sets()


def download_data_sets():
	"""Downloads the datasets"""
	# for resource in [shopify.Customer, shopify.Product, shopify.Order]:
	for resource in [shopify.Order]:
		download_shopify_resource(resource)

def download_shopify_resource(shopify_resource: Type[ShopifyResource]):
	data = []
	session = requests.Session()  # Persistent connection
	headers = {"Content-Type": "application/json"}

	# Initial API endpoint. Adjust `status` and other query params as needed.
	# url = f"https://gelous.myshopify.com/admin/api/2024-01/{shopify_resource.plural}.json?limit=250&status=open"
	url = f"{shopify_resource._site}/api/2024-01/{shopify_resource.plural}.json?limit=250&status=open"
	print(url)
	while url:
		response = session.get(url, headers=headers)
		if response.status_code == 200:
			json_response = response.json()
			resources = json_response.get(shopify_resource.plural)
			data.extend(resources)

			# Extracting next page URL from 'Link' header
			links = response.headers.get('Link', '')
			next_url = None
			for link in links.split(','):
				if 'rel="next"' in link:
					next_url = link.split(';')[0].strip('<> ')
					break

			# Update URL for the next iteration or break if no next page
			url = next_url if next_url else None
		else:
			logging.error(f"Failed to retrieve {shopify_resource.plural}, status code: {response.status_code}")
			break

	# Save data logic remains the same
	relative_filepath = Path(f"{shopify_resource.plural}-v1.json.gz")
	with tempfile.TemporaryDirectory() as tmp_dir:
		tmp_filepath = Path(tmp_dir, relative_filepath)
		tmp_filepath.parent.mkdir(exist_ok=True, parents=True)
		with gzip.open(str(tmp_filepath), 'wt') as tmp_file:
			tmp_file.write(json.dumps(data))
		shutil.move(str(tmp_filepath), str(relative_filepath))