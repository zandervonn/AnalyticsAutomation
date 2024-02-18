import pandas as pd
import matplotlib.pyplot as plt

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