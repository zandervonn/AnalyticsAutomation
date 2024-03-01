import time
import requests

def get_cin7_data(api_key, rows_per_call=250):
	base_url = 'https://api.cin7.com/api/v1/'
	endpoint = "Products"
	headers = {
		'Authorization': api_key,
	}

	all_data = []
	page = 1

	while True and page < 3:
		url = f'{base_url}{endpoint}?page={page}&rows={rows_per_call}'
		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			data = response.json()
			all_data.extend(data)
			if len(data) < rows_per_call:
				break
			page += 1
			print("Page ", page)
			time.sleep(1)  # Delay to comply with rate limiting
		else:
			print(f'Error: {response.status_code}')
			return None

	return all_data