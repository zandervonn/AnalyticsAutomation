from datetime import datetime, timedelta

import requests
import pandas as pd

def get_meta_insights(meta_token, id_number, metrics, since, until):
	base_url = f'https://graph.facebook.com/v19.0/{id_number}/insights'
	# Extract base metric names for the API request
	base_metrics = set(metric.split('.')[0] for metric in metrics)

	df = pd.DataFrame()  # Initialize an empty DataFrame

	# Convert since and until strings to datetime objects
	since_date = datetime.strptime(since, '%Y-%m-%dT%H:%M:%S')
	until_date = datetime.strptime(until, '%Y-%m-%dT%H:%M:%S')

	print(metrics)

	# Split the time range into one-week intervals
	while since_date < until_date:
		week_until_date = min(since_date + timedelta(days=7), until_date)
		params = {
			'access_token': meta_token,
			'metric': ','.join(base_metrics),
			'period': 'day',
			'since': since_date.strftime('%Y-%m-%d'),
			'until': week_until_date.strftime('%Y-%m-%d'),
		}
		url = base_url  # Reset the URL to the base URL for each interval

		while True:
			response = requests.get(url, params=params, timeout=60)
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

			break

		# Move to the next one-week interval
		since_date = week_until_date

	# Pivot the DataFrame
	df_pivot = df.pivot(index='end_time', columns='metric', values='value').reset_index()
	return df_pivot

def get_posts(meta_token, page_id, since, until):
	base_url = f'https://graph.facebook.com/v19.0/{page_id}/posts'
	params = {
		'access_token': meta_token,
		'since': since,
		'until': until,
		'fields': 'id,message,created_time'
	}
	response = requests.get(base_url, params=params)
	posts_data = response.json()
	return posts_data['data']

def get_videos(meta_token, page_id, since, until):
	base_url = f'https://graph.facebook.com/v19.0/{page_id}/videos'
	params = {
		'access_token': meta_token,
		'since': since,
		'until': until,
		'fields': 'id,description,created_time'
	}
	response = requests.get(base_url, params=params)
	posts_data = response.json()
	return posts_data['data']

def get_media(meta_token, page_id, since, until):
	base_url = f'https://graph.facebook.com/v19.0/{page_id}/media'
	params = {
		'access_token': meta_token,
		'since': since,
		'until': until,
		'fields': 'id,message,created_time'
	}
	response = requests.get(base_url, params=params)
	posts_data = response.json()
	return posts_data['data']

def get_insights(meta_token, post_id, metrics):
	insights_url = f'https://graph.facebook.com/v19.0/{post_id}/insights'
	params = {
		'access_token': meta_token,
		'metric': metrics
	}
	response = requests.get(insights_url, params=params)
	insights_data = response.json()
	if 'data' in insights_data:
		return {insight['name']: insight['values'][0]['value'] if insight['values'] else None for insight in insights_data['data']}
	else:
		print(f"No insights data available for post ID: {post_id}")
		return {}

def get_video_insights(meta_token, post_id):
	insights_url = f'https://graph.facebook.com/v19.0/{post_id}/video_insights'
	params = {
		'access_token': meta_token,
	}
	response = requests.get(insights_url, params=params)
	insights_data = response.json()
	return parse_insights(insights_data, post_id)

def parse_insights(insights_data, post_id):
	if 'data' in insights_data:
		parsed_data = {}
		for insight in insights_data['data']:
			# Handle the case where 'values' contains multiple values
			if insight['values']:
				value = insight['values'][0]['value']
				if isinstance(value, dict):
					# If the value is a dictionary, store each key-value pair separately
					for key, val in value.items():
						parsed_data[f"{insight['name']}.{key}"] = val
				else:
					# If the value is not a dictionary, store it directly
					parsed_data[insight['name']] = value
			else:
				parsed_data[insight['name']] = None
		return parsed_data
	else:
		print(f"No insights data available for post ID: {post_id}")
		return {}

def get_facebook_metric_count(meta_token, post_id, metric):
	url = f'https://graph.facebook.com/v19.0/{post_id}/{metric}'
	params = {
		'access_token': meta_token,
		'summary': 'true'
	}
	response = requests.get(url, params=params)
	data = response.json()
	return data['summary']['total_count']

def get_instagram_post_metrics(meta_token, post_id, metrics):
	url = f'https://graph.facebook.com/v19.0/{post_id}/insights'

	metrics_str = ','.join(metrics)
	params = {
		'access_token': meta_token,
		'metric': metrics_str
	}

	response = requests.get(url, params=params)
	data = response.json()
	print(data)
	return data

def get_instagram_post_headers(meta_token, post_id, metrics):
	url = f'https://graph.facebook.com/v19.0/{post_id}'

	metrics_str = ','.join(metrics)
	params = {
		'access_token': meta_token,
		'fields': metrics_str
	}

	response = requests.get(url, params=params)
	data = response.json()
	return data

def get_facebook_posts_and_insights(meta_token, page_id, metrics, since, until):
	posts = get_posts(meta_token, page_id, since, until)
	post_insights = []

	for post in posts:
		post_id = post['id']
		insights = get_insights(meta_token, post_id, metrics)
		comments_count = get_facebook_metric_count(meta_token, post_id, 'comments')
		likes_count = get_facebook_metric_count(meta_token, post_id, 'likes')
		insights['comments_count'] = comments_count
		insights['likes_count'] = likes_count
		post_insights.append({
			'post_id': post_id,
			'message': post.get('message', ''),
			'created_time': post['created_time'],
			**insights
		})

	df = pd.DataFrame(post_insights)
	return df

def get_facebook_video_insights(meta_token, page_id, since, until):
	posts = get_videos(meta_token, page_id, since, until)
	post_insights = []

	for post in posts:
		post_id = post['id']
		post_message = post.get('description', '')
		post_updated_time = post['created_time']
		insights = get_video_insights(meta_token, post_id)
		post_insights.append({
			'post_id': post_id,
			'description': post_message,
			'created_time': post_updated_time,
			**insights
		})

	df = pd.DataFrame(post_insights)
	return df

def get_insta_posts_and_insights(meta_token, page_id, metrics, since, until):
	posts = get_media(meta_token, page_id, since, until)
	post_insights = []

	for post in posts:
		post_id = post['id']
		specified_fields = ['timestamp', 'id', 'caption']
		header_metrics = [metric for metric in metrics if metric in specified_fields]
		post_metrics = [metric for metric in metrics if metric not in specified_fields]

		insta_headers = get_instagram_post_headers(meta_token, post_id, header_metrics)
		insta_metrics = get_instagram_post_metrics(meta_token, post_id, post_metrics)
		insta_metrics = parse_insights(insta_metrics, post_id)

		# Merge the headers and metrics dictionaries
		combined_insights = {**insta_headers, **insta_metrics}
		post_insights.append(combined_insights)

	df = pd.DataFrame(post_insights)
	return df


def split_insights_to_sheets(df, insights_pages):
	# Dictionary to store the DataFrames
	dfs = {}

	# Filter out the columns that actually exist in the DataFrame
	existing_columns = [col for col in insights_pages if col in df.columns]

	# Save the original DataFrame with list data removed
	filtered_df = df.drop(columns=existing_columns)
	dfs['Summary'] = filtered_df

	# Iterate over each insight page and create a separate DataFrame
	for page in existing_columns:
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

def clean_facebook_video_df(df):
	# Combine the two columns and insert the new column at the index of the second one
	index_of_second_column = df.columns.get_loc('post_video_likes_by_reaction_type.REACTION_LIKE')
	df.insert(
		index_of_second_column,
		'post_video_likes_and_loves',
		df['post_video_likes_by_reaction_type.REACTION_LOVE'] + df['post_video_likes_by_reaction_type.REACTION_LIKE']
	)

	# Drop the original columns
	df.drop(['post_video_likes_by_reaction_type.REACTION_LOVE', 'post_video_likes_by_reaction_type.REACTION_LIKE'], axis=1, inplace=True)

	return df