# have access
# can add new connection
# 3 per second, 60 per minute and 5000 per day.
# recommend only polling most recent data


def get_orders(shopify_api_key, shopify_password, shopify_url, page_limit=-1):
	base_url = f"https://{shopify_api_key}:{shopify_password}@{shopify_url}/admin/api/2024-01/"
	endpoint = "orders.json?limit=250&status=any"
	return fetch_pages(base_url, endpoint, page_limit)