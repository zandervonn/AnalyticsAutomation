import pandas as pd
import matplotlib.pyplot as plt
import re
from urllib.parse import urlparse, parse_qs


def analyze_repurchase_trends(csv_file_path):
	# Sample DataFrame
	df = pd.read_csv(csv_file_path)

	# Ensure 'Date' is in datetime format
	df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)

	# Sort by CustomerID and Date
	df.sort_values(by=['Customer ID', 'Date'], inplace=True)

	# Calculate the difference in days between consecutive purchases for each customer
	df['DaysBetweenPurchases'] = df.groupby('Customer ID')['Date'].diff().dt.days

	# Filter out first purchase for each customer since it doesn't have a preceding purchase
	df_filtered = df.dropna(subset=['DaysBetweenPurchases']).copy()

	# Calculate average days between purchases per period (e.g., monthly)
	df_filtered['YearMonth'] = df_filtered['Date'].dt.to_period('M')
	average_time_between_purchases = df_filtered.groupby('YearMonth')['DaysBetweenPurchases'].mean()

	# Check if all dates are the same, which would cause the plotting issue
	if len(average_time_between_purchases.index.unique()) <= 1:
		print("Not enough data to plot over time.")
	else:
		# Plotting
		average_time_between_purchases.plot(kind='line', figsize=(10, 6))
		plt.title('Average Time Between Repurchases Over Time')
		plt.xlabel('Time Period')
		plt.ylabel('Average Days Between Purchases')
		plt.grid(True)
		plt.show()

def shopify_clean_df(df):
	df[['channel', 'campaign']] = df['landing_site'].apply(lambda x: extract_channel_and_campaign(x) if pd.notna(x) else ('other', None)).apply(pd.Series)

	return df

def extract_channel_and_campaign(url):
	# Default values
	channel = 'other'
	campaign = None

	# Parse the URL
	parsed_url = urlparse(url)
	query_params = parse_qs(parsed_url.query)

	# Ensure values are strings
	query_params = {k: [v.decode() if isinstance(v, bytes) else v for v in vals] for k, vals in query_params.items()}

	# Check for known channels
	if 'utm_source' in query_params:
		source = query_params['utm_source'][0].lower()
		if 'google' in source:
			channel = 'google'
		elif 'facebook' in source:
			channel = 'facebook'
		elif 'insta' in source:
			channel = 'insta'
		elif 'klaviyo' in source:
			channel = 'klaviyo'
		elif 'tiktok' in source:
			channel = 'tiktok'
		elif 'snap' in source:
			channel = 'snap'

	# Extract campaign data using regex
	campaign_match = re.search(r'utm_campaign=([^&]*)', url)
	if campaign_match:
		campaign = campaign_match.group(1)

	# Return the extracted channel and campaign
	return channel, campaign