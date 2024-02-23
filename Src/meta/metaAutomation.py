import time
import requests
import pandas as pd


def get_meta_page_info(meta_token, id_number, page_limit):
	url = f'https://graph.facebook.com/v19.0/{id_number}/insights'
	#https://developers.facebook.com/docs/graph-api/reference/v19.0/insights
	metrics = [
		# 'page_total_actions',
		# 'page_engaged_users',
		# 'page_impressions_organic_v2',
		'page_fan_removes_unique',
		# 'page_fans_by_like_source'
		# 'page_impressions',
		# 'page_views_total',
		# 'page_fan_adds_unique'

	]
	params = {
		'access_token': meta_token,
		'metric': ','.join(metrics),
		'period': 'week',
		# 'date_preset': 'last_week'
	}

	# Initialize an empty DataFrame
	df = pd.DataFrame()
	page_count = 1
	# Loop through pages
	while True and (page_count < page_limit or page_limit == -1):
		response = requests.get(url, params=params)
		data = response.json()
		print("Getting page", page_count)
		print("Page body: ", data)

		# Extract data and append to DataFrame
		for item in data['data']:

			df = df.append(pd.json_normalize(item['values']), ignore_index=True)

		# Check for next page
		if 'paging' in data and 'next' in data['paging']:
			url = data['paging']['next']
			page_count += 1
		else:
			break

	return df

def get_instagram_metrics(meta_token, id_number):
	url = f'https://graph.facebook.com/v19.0/{id_number}/insights'
	metrics = [
		# 'profile_likes'
		# 'reach',
		# 'follower_count',
		# 'email_contacts',
		"page_impressions_unique"
		# 'phone_call_clicks',
		# 'text_message_clicks',
		# 'get_directions_clicks',
		# 'website_clicks',
		# 'profile_views'
	]
	params = {
		'access_token': meta_token,
		'metric': ','.join(metrics),
		'period': 'week'
	}
	response = requests.get(url, params=params)
	print("Request URL:", response.request.url)
	print("Request Headers:", response.request.headers)
	print("Request Body:", response.request.body)
	print("Response Body:", response.json())
	return response.json()
