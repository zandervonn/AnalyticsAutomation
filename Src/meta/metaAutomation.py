import time
import requests

def get_sort_lived_access_token(app_id, app_secret):
	url = 'https://graph.facebook.com/oauth/access_token'
	payload = {
		'grant_type': 'client_credentials',
		'client_id': app_id,
		'client_secret': app_secret
	}
	response = requests.post(url, params=payload)

	print("Request URL:", response.request.url)
	print("Request Headers:", response.request.headers)
	print("Request Body:", response.request.body)
	print("Response Body:", response.json())

	return response.json()['access_token']

def get_long_lived_access_token(short_lived_access_token, app_id, app_secret):
	url = f"https://graph.facebook.com/v19.0/oauth/access_token"
	params = {
		"grant_type": "fb_exchange_token",
		"client_id": app_id,
		"client_secret": app_secret,
		"fb_exchange_token": short_lived_access_token
	}
	response = requests.get(url, params=params)
	response_data = response.json()

	print("Request URL:", response.request.url)
	print("Request Headers:", response.request.headers)
	print("Request Body:", response.request.body)
	print("Response Body:", response.json())

	if "access_token" in response_data:
		return response_data["access_token"]
	else:
		raise Exception(f"Error getting long-lived access token: {response_data.get('error')}")

def get_long_lived_page_access_token(app_scoped_user_id, long_lived_user_access_token):
	url = f"https://graph.facebook.com/v19.0/{my_personal_id}/accounts?access_token={long_lived_user_access_token}"
	response = requests.get(url)
	response_data = response.json()

	print("Request URL:", response.request.url)
	print("Request Headers:", response.request.headers)
	print("Request Body:", response.request.body)
	print("Response Body:", response.json())

	if "data" in response_data and len(response_data["data"]) > 0:
		# Assuming you want the access token for the first page in the list
		return response_data["data"][0]["access_token"]
	else:
		raise Exception(f"Error getting long-lived page access token: {response_data.get('error')}")


def get_meta_page_info(meta_token, id_number, page_limit=-1):
	url = f'https://graph.facebook.com/v19.0/{id_number}/insights'
	metrics = [
		'page_total_actions',
		# 'page_engaged_users',
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
	response = requests.get(url, params=params)
	print("Request URL:", response.request.url)
	print("Request Headers:", response.request.headers)
	print("Request Body:", response.request.body)
	print("Response Body:", response.json())
	return response

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
