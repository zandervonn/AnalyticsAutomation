# have access
# can add new connection
# 3 per second, 60 per minute and 5000 per day.
# recommend only polling most recent data


import requests

def get_cin7_data(api_key):
	#todo only returning 50, check this is all there should be
	#todo check that the values coming back look correct
	base_url = 'https://api.cin7.com/api/v1/'
	headers = {
		'Authorization': api_key,
		'rows': '250'
	}
	endpoint = f"Products"
	url = f'{base_url}{endpoint}'

	response = requests.get(url, headers=headers)
	if response.status_code == 200:
		return response.json()
	else:
		print(f'Error: {response.status_code}')
		return None