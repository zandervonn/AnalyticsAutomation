import pandas as pd
import matplotlib.pyplot as plt
import json
import csv

from io import StringIO

def clean_json(all_orders, defined_subheaders):
	# Split the headers into top-level and nested fields
	top_level_fields = [header for header in defined_subheaders if '.' not in header]
	nested_fields = {header.split('.')[0]: [] for header in defined_subheaders if '.' in header}
	for header in defined_subheaders:
		parts = header.split('.')
		if len(parts) > 1:
			nested_fields[parts[0]].append(parts[1])

	# Process each order
	cleaned_orders = []
	for order in all_orders:
		cleaned_order = {}
		# Keep only the top-level fields
		for field in top_level_fields:
			if field in order:
				cleaned_order[field] = order[field]

		# Process nested fields
		for nested_field, subfields in nested_fields.items():
			if nested_field in order:
				if isinstance(order[nested_field], list):  # If the nested field is a list of dictionaries
					cleaned_order[nested_field] = [
						{subfield: item.get(subfield, None) for subfield in subfields}
						for item in order[nested_field]
					]
				elif isinstance(order[nested_field], dict):  # If the nested field is a single dictionary
					cleaned_order[nested_field] = {
						subfield: order[nested_field].get(subfield, None) for subfield in subfields
					}

		cleaned_orders.append(cleaned_order)

	return cleaned_orders

def json_to_csv(json_data):
	# Check if the JSON data is empty
	if not json_data:
		return ""

	# Determine the headers from the first item in the JSON data
	headers = json_data[0].keys()

	# Create a StringIO object to write the CSV data
	output = StringIO()
	writer = csv.DictWriter(output, fieldnames=headers)

	# Write the headers and data rows
	writer.writeheader()
	for row in json_data:
		writer.writerow(row)

	# Get the CSV string from the StringIO object
	csv_string = output.getvalue()
	output.close()

	return csv_string

def save_df_to_csv(df, file_path):
	df.to_csv(file_path, index=False)
	print(f"CSV saved to {file_path}")

def load_csv(path):
	return pd.read_csv(path)

def analyze_repurchase_trends(csv_file_path):

	# Sample DataFrame
	df = pd.read_csv(csv_file_path)

	# Ensure 'Date' is in datetime format
	df['Date'] = pd.to_datetime(df['Date'], utc=True)

	# Sort by CustomerID and Date
	df.sort_values(by=['Customer ID', 'Date'], inplace=True)

	# Calculate the difference in days between consecutive purchases for each customer
	df['DaysBetweenPurchases'] = df.groupby('Customer ID')['Date'].diff().dt.days

	# Filter out first purchase for each customer since it doesn't have a preceding purchase
	df_filtered = df.dropna(subset=['DaysBetweenPurchases'])

	# Calculate average days between purchases per period (e.g., monthly)
	df_filtered['YearMonth'] = df_filtered['Date'].dt.to_period('M')
	average_time_between_purchases = df_filtered.groupby('YearMonth')['DaysBetweenPurchases'].mean()

	# Plotting
	average_time_between_purchases.plot(kind='line', figsize=(10, 6))
	plt.title('Average Time Between Repurchases Over Time')
	plt.xlabel('Time Period')
	plt.ylabel('Average Days Between Purchases')
	plt.grid(True)
	plt.show()