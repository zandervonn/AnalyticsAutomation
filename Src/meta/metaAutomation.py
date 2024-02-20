import time
import requests



def get_meta_page_info(meta_token, id_number, page_limit=-1):
	url = f'https://graph.facebook.com/v19.0/{id_number}/insights/'
	endpoint = "page_total_actions"
	# endpoint = ""
	params = {
		# 'name': 'page_total_actions',
		# 'debug': 'all',
		# 'date_preset': 'last_7_days',
		# 'metadata': '1',
		'access_token': meta_token
	}
	# url = base_url + endpoint
	response = requests.get(url+endpoint, params=params)
	print("Request URL:", response.request.url)
	print("Request Headers:", response.request.headers)
	print("Request Body:", response.request.body)
	print(response.json())
	return response


	# return get_meta_paginated_data(url, page_limit)

def get_meta_paginated_data(url, max_pages=None):
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
			page_data = data.get('', [])
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