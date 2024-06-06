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
		'fields': 'id,message,created_time,media_type'
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
	print("metrics",metrics)
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
	print("headers", metrics)
	print(data)
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

def get_insta_video_insights(meta_token, page_id, since, until):
	posts = get_media(meta_token, page_id, since, until)
	post_insights = []

	# Define metrics and headers for each media type
	media_details = {
		'VIDEO': {
			'header_metrics': ['timestamp', 'id', 'media_type', 'caption'],
			'post_metrics': ['reach', 'saved', 'likes', 'comments', 'shares', 'plays', 'total_interactions', 'ig_reels_video_view_total_time', 'ig_reels_avg_watch_time', 'clips_replays_count', 'ig_reels_aggregated_all_plays_count']
		},
	}

	for post in posts:
		post_id = post['id']
		media_type = post.get('media_type')
		if media_type == 'VIDEO':
			details = media_details.get('VIDEO')

			# Fetch post headers and metrics
			insta_headers = get_instagram_post_headers(meta_token, post_id, details['header_metrics'])
			insta_metrics = get_instagram_post_metrics(meta_token, post_id, details['post_metrics'])

			# Parse insights and combine headers with metrics
			insta_metrics = parse_insights(insta_metrics, post_id)

			combined_insights = {**insta_headers, **insta_metrics}
			post_insights.append(combined_insights)

	# Convert the list of dictionaries into a DataFrame
	df = pd.DataFrame(post_insights)
	return df

def get_insta_image_insights(meta_token, page_id, since, until):
	posts = get_media(meta_token, page_id, since, until)
	post_insights = []

	# Define metrics and headers for each media type
	media_details = {
		'CAROUSEL_ALBUM': {
			'header_metrics': ['timestamp', 'id', 'media_type', 'caption', 'like_count', 'comments'],
			'post_metrics': ['impressions', 'reach', 'saved', 'total_interactions']
		},
		'IMAGE': {
			'header_metrics': ['timestamp', 'id', 'media_type', 'caption'],
			'post_metrics': ['impressions', 'reach', 'saved', 'likes', 'comments', 'shares', 'total_interactions']
		}
	}

	for post in posts:
		post_id = post['id']
		media_type = post.get('media_type')
		if media_type == 'IMAGE' or media_type == 'CAROUSEL_ALBUM':
			details = media_details.get(media_type)

			# Fetch post headers and metrics
			insta_headers = get_instagram_post_headers(meta_token, post_id, details['header_metrics'])
			insta_metrics = get_instagram_post_metrics(meta_token, post_id, details['post_metrics'])

			# Simplify comments to count only
			if 'comments' in insta_headers:
				insta_headers['comments'] = len(insta_headers['comments'].get('data', [])) - 1

			# Parse insights and combine headers with metrics
			insta_metrics = parse_insights(insta_metrics, post_id)
			combined_insights = {**insta_headers, **insta_metrics}
			post_insights.append(combined_insights)


	# Convert the list of dictionaries into a DataFrame
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


def clean_facebook_post_df(df):
	# Make a deep copy of the DataFrame to ensure operations are done on a new DataFrame
	df = df.copy()

	# Merge reaction columns if they exist
	if 'post_video_likes_by_reaction_type.REACTION_LOVE' in df.columns and 'post_video_likes_by_reaction_type.REACTION_LIKE' in df.columns:
		index_of_second_column = df.columns.get_loc('post_video_likes_by_reaction_type.REACTION_LIKE')
		df.insert(
			index_of_second_column,
			'post_video_likes_and_loves',
			df['post_video_likes_by_reaction_type.REACTION_LOVE'] + df['post_video_likes_by_reaction_type.REACTION_LIKE']
		)
		df.drop(['post_video_likes_by_reaction_type.REACTION_LOVE', 'post_video_likes_by_reaction_type.REACTION_LIKE'], axis=1, inplace=True)

	# Convert time from ms to s for relevant columns
	if 'post_video_avg_time_watched' in df.columns:
		df['avg_time_watched_s'] = df['post_video_avg_time_watched'] / 1000
		df.drop('post_video_avg_time_watched', axis=1, inplace=True)

	if 'post_video_view_time' in df.columns:
		df['total_view_time_s'] = df['post_video_view_time'] / 1000
		df.drop('post_video_view_time', axis=1, inplace=True)

	# Drop rows with all NaN values except the date column
	date_column = 'created_time'
	cols_to_check = df.columns.difference([date_column])
	df = df.dropna(subset=cols_to_check, how='all')

	# Fill remaining NaN values with '0'
	df.fillna('0', inplace=True)

	# Trim and debug captions
	caption_column = 'message' if 'message' in df.columns else 'description' if 'description' in df.columns else None
	if caption_column:
		df[caption_column] = df[caption_column].apply(lambda x: trim_caption(x))

	return df

def trim_caption(caption):
	if pd.notna(caption):
		# Strip to remove leading/trailing whitespace and split on newline
		trimmed = caption.strip().split('\n', 1)[0]
		return trimmed
	return caption

def clean_insta_video_df(insta_df):
	"""
	Clean and convert Instagram video data within a DataFrame.

	Parameters:
	insta_df (pd.DataFrame): The DataFrame containing Instagram video insights.

	Returns:
	pd.DataFrame: The cleaned DataFrame with time conversions applied.
	"""
	# Convert 'ig_reels_video_view_total_time' from ms to s and rename the column
	if 'ig_reels_video_view_total_time' in insta_df.columns:
		insta_df['video_view_time_s'] = insta_df['ig_reels_video_view_total_time'] / 1000
		insta_df.drop('ig_reels_video_view_total_time', axis=1, inplace=True)

	# Convert 'ig_reels_avg_watch_time' from ms to s and rename the column
	if 'ig_reels_avg_watch_time' in insta_df.columns:
		insta_df['avg_watch_time_s'] = insta_df['ig_reels_avg_watch_time'] / 1000
		insta_df.drop('ig_reels_avg_watch_time', axis=1, inplace=True)

	# Trim captions
	if 'caption' in insta_df.columns:
		insta_df['caption'] = insta_df['caption'].apply(lambda x: x.split('\n', 1)[0] if pd.notna(x) else x)

	return insta_df


def clean_insta_image_df(insta_df):
	"""
	Clean and adjust the Instagram image data within a DataFrame by merging likes counts
	and calculating shares when necessary.

	Parameters:
	insta_df (pd.DataFrame): The DataFrame containing Instagram image insights.

	Returns:
	pd.DataFrame: The cleaned DataFrame with combined likes and calculated shares.
	"""
	# Combine 'like_count' and 'likes' into one 'likes' column
	if 'like_count' in insta_df.columns and 'likes' in insta_df.columns:
		insta_df['likes'] = insta_df['like_count'].fillna(0) + insta_df['likes'].fillna(0)
		insta_df.drop('like_count', axis=1, inplace=True)
	elif 'like_count' in insta_df.columns:
		insta_df.rename(columns={'like_count': 'likes'}, inplace=True)

	# Calculate 'shares' if it is blank
	if 'shares' in insta_df.columns:
		for idx, row in insta_df.iterrows():
			if pd.isna(row['shares']) or row['shares'] == '':
				# Ensure values are not NaN before subtraction to avoid negative or NaN results
				comments = row.get('comments', 0) or 0
				likes = row.get('likes', 0) or 0
				saved = row.get('saved', 0) or 0
				total_interactions = row.get('total_interactions', 0) or 0
				insta_df.at[idx, 'shares'] = total_interactions - (comments + likes + saved)

	# Trim captions
	if 'caption' in insta_df.columns:
		insta_df['caption'] = insta_df['caption'].apply(lambda x: x.split('\n', 1)[0] if pd.notna(x) else x)


	return insta_df