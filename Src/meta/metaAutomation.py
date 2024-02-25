import requests
import pandas as pd

def get_meta_insights(meta_token, id_number, metrics, since, until, page_limit):
	url = f'https://graph.facebook.com/v19.0/{id_number}/insights'
	params = {
		'access_token': meta_token,
		'metric': ','.join(metrics),
		'period': 'day',
		'since': since,
		'until': until
	}

	df = pd.DataFrame()  # Initialize an empty DataFrame
	page_count = 0

	while True:
		response = requests.get(url, params=params)
		data = response.json()

		# Check if the response contains 'data'
		if 'data' not in data:
			if 'error' in data:
				# Log the error and break or raise an exception
				error_message = data['error'].get('message', 'No error message provided')
				raise Exception(f"Error fetching Meta insights: {error_message}")
			else:
				# If there's no 'data' or 'error', it could be another issue
				raise Exception("Unknown error occurred when fetching Meta insights")

		# Extract data and append to DataFrame
		for item in data['data']:
			for value in item['values']:
				df = df.append({
					'metric': item['name'],
					'end_time': value['end_time'],
					'value': value['value']
				}, ignore_index=True)

		# Implement paging logic if necessary
		# if 'paging' in data and 'next' in data['paging']:
		#     url = data['paging']['next']
		#     page_count += 1
		# else:
		break

	return df
