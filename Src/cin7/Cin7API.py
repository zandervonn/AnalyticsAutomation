# have access
# can add new connection
# 3 per second, 60 per minute and 5000 per day.
# recommend only polling most recent data


import requests

def get_cin7_data(api_key):
	base_url = 'https://api.cin7.com/api/v1/'
	headers = {
		'Authorization': api_key
	}
	endpoint = f"Products"
	# Products?fields={fields}&where={where}&order={order}&page={page}&rows={rows}
	url = f'{base_url}{endpoint}'

	response = requests.get(url, headers=headers)
	print("Request URL:", response.request.url)
	print("Request Headers:", response.request.headers)
	print("Request Body:", response.request.body)
	print("Response Body:", response.json())
	if response.status_code == 200:
		return response.json()
	else:
		print(f'Error: {response.status_code}')
		return None