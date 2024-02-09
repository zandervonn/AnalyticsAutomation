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



# Function to get all order history
def get_all_orders():
	orders = []
	page = 1
	while True:
		url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/{version}/orders.json?page={page}&limit=250"
		response = requests.get(url, headers=headers)
		if response.status_code == 200:
			data = response.json()
			orders.extend(data['orders'])
			if not data['orders']:
				break  # No more orders to fetch
			page += 1
		else:
			print(f"Failed to retrieve orders, status code: {response}")
			break
	return orders


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

def test_connection():
	# shop_url = "https://{api_key}:{password}@{shopurl}/admin/".format(api_key=access.shopify_api_key(),
	#                                                                  password=access.shopify_password(),
	#                                                                  shopurl=access.shopify_url())
	shop_url = f"https://{access.shopify_api_key()}:{access.shopify_password()}@{access.shopify_url()}/admin/api/{version}/shop.json"

	# session = shopify.Session(shop_url, version="2024-01")
	# shopify.ShopifyResource.activate_session(session)
	# shop = shopify.Shop.current

	shopify.ShopifyResource.set_site(shop_url)
	shop = shopify.Shop.current

	orders = shopify.Order.find(id="5638484230446")
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

def download_shopify_resource2(shopify_resource: Type[ShopifyResource]):
	data = []
	page = 1
	previous_page = 0
	max_attempts = 1
	while True:
		number_of_attempts = 0
		while True:
			try:
				resource = shopify_resource.find(limit=250, page=page, status="open")
				if len(resource) > 0 or (previous_page == page):
					break
			except:
				if number_of_attempts < max_attempts:
					duration = 4 * number_of_attempts + 1
					logging.info(
						'Loading shopify data retry #{attempt} in {duration} seconds'.format(attempt=number_of_attempts,
						                                                                     duration=duration))
					sleep(duration)
					number_of_attempts += 1
				else:
					raise

			previous_page = page
		if len(resource) > 0:
			previous_page = page
			data.extend(resource)
			page += 1
		else:
			relative_filepath = Path(access.data_dir(),
			                         '{resource_name}-{version}.json.gz'.format(
				                         resource_name=shopify_resource.plural,
				                         version="v1"))
			# filepath = ensure_data_directory(relative_filepath)
			with tempfile.TemporaryDirectory() as tmp_dir:
				tmp_filepath = Path(tmp_dir, relative_filepath)
				tmp_filepath.parent.mkdir(exist_ok=True, parents=True)
				with gzip.open(str(tmp_filepath), 'wt') as tmp_ad_performance_file:
					tmp_ad_performance_file.write(json.dumps([c.to_dict() for c in data]))
			shutil.move(str(tmp_filepath), str(relative_filepath))
			break