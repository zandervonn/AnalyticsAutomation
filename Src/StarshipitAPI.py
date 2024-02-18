# have access
# 2 requests per second
import requests

from Src.gitignore import access

# url = 'https://api.starshipit.com/api/orders/unshipped'
url = 'https://api.starshipit.com/api/orders/unshipped?since_order_date=2020-10-12T07%3A20%3A50.52Z&since_last_updated=2020-10-12T07%3A20%3A50.52Z&ids_only=false&limit=50&page=1'
headers = {
	'Content-Type': 'application/json',
	'StarShipIT-Api-Key': f'{access.starshipit_api_key()}',
	'Ocp-Apim-Subscription-Key': f'{access.starshipit_subscription_key()}'
}
# params = {
# 	'since_order_date': '2020-10-12T07:20:50.52Z',
# 	'since_last_updated': '2020-10-12T07:20:50.52Z',
# 	'ids_only': False,
# 	'limit': 50,
# 	'page': 1
# }

def get_starshipit_orders():
	# response = requests.get(url, headers=headers, params=params)
	response = requests.get(url, headers=headers)

	if response.status_code == 200:
		orders = response.json()
		print(orders)
	else:
		print(f'Failed to get orders: {response.status_code} - {response.text}')