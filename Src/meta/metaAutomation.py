import requests
import pandas as pd

def get_meta_insights(meta_token, id_number, metrics, since, until, page_limit):
	# todo pagination
	# todo get posts and get stats for the post
	url = f'https://graph.facebook.com/v19.0/{id_number}/insights'
	# Extract base metric names for the API request
	base_metrics = set(metric.split('.')[0] for metric in metrics)
	params = {
		'access_token': meta_token,
		'metric': ','.join(base_metrics),
		'period': 'day',
		'since': since,
		'until': until,
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
				new_row = pd.DataFrame({
					'metric': [item['name']],
					'end_time': [value['end_time']],
					'value': [value['value']]
				})
				df = pd.concat([df, new_row], ignore_index=True)

		# Implement paging logic if necessary
		# if 'paging' in data and 'next' in data['paging']:
		#     url = data['paging']['next']
		#     page_count += 1
		# else:
		break

	# Pivot the DataFrame
	df_pivot = df.pivot(index='end_time', columns='metric', values='value').reset_index()
	return df_pivot

def split_insights_to_sheets(df, insights_pages):
	# Dictionary to store the DataFrames
	dfs = {}

	# Save the original DataFrame with list data removed
	filtered_df = df.drop(columns=insights_pages)
	dfs['Summary'] = filtered_df

	# Iterate over each insight page and create a separate DataFrame
	for page in insights_pages:
		if page in df.columns:
			# Extract the list data and corresponding end_time values
			page_data = df[['end_time', page]].dropna()
			list_data = page_data[page].tolist()
			end_time_data = page_data['end_time'].tolist()

			# Convert the list data to a DataFrame and add the end_time column
			expanded_df = pd.DataFrame(list_data)
			expanded_df.insert(0, 'end_time', end_time_data)

			# Add the expanded DataFrame to the dictionary
			dfs[page] = expanded_df

	return dfs