import pandas as pd
import numpy as np
import json
import pandas as pd
import re
import ast

shopify_defined_headers = [
	'checkout_id', 'confirmation_number', 'contact_email', 'created_at',
	'current_subtotal_price', 'current_total_discounts', 'current_total_price',
	'current_total_tax', 'discount_codes', 'landing_site', 'name', 'note',
	'order_number', 'payment_gateway_names', 'total_discounts', 'total_tip_received',
	'total_weight', 'customer', 'fulfillments', 'line_items'
]

def keep_defined_headers(df, defined_headers):
	# Drop columns that are not in the defined headers list
	df = df[defined_headers]
	return df

# Define cleaning functions
def remove_brackets(text):
	if isinstance(text, str):  # Ensure the text is a string
		return text.replace("(", "").replace(")", "")
	return text

def make_lists_normal(text):
	if isinstance(text, str):  # Ensure the text is a string
		return text.replace("[", "").replace("]", "").replace("'", "")
	return text

def clear_empty_columns(df):
	return df.replace('', np.nan).dropna(axis=1, how='all')


def split_columns(df, column, keys):
	# Define a new DataFrame to hold the split columns
	new_cols = pd.DataFrame(index=df.index)

	# Iterate over each row and process the string in the specified column
	for index, row in df.iterrows():
		# Check if the value is a string and not NaN
		if pd.notna(row[column]):
			# Remove curly braces and split the string on ','
			entries = row[column].strip('{}').split(', ')
			# Create a dictionary from the string
			entry_dict = {}
			for entry in entries:
				# Split the entry on ':' to get key-value pairs
				key_val_pair = entry.split(': ')
				if len(key_val_pair) == 2:
					key, value = key_val_pair
					entry_dict[key.strip()] = value.strip()

			# Assign the values to the new columns based on keys
			for key in keys:
				new_col_name = f"{column}.{key}"
				new_cols.at[index, new_col_name] = entry_dict.get(key)

	# Concatenate the new columns to the original DataFrame
	df = pd.concat([df, new_cols], axis=1)

	# Drop the original column if no longer needed
	df.drop(columns=[column], inplace=True)

	return df

def parse_line_item_string(line_item_str):
	# Handle None or NaN values
	if pd.isnull(line_item_str):
		return [], []

	# Split the string into list of items
	items = line_item_str.strip(' ').split('}, {')

	# Initialize lists to hold extracted names and prices
	names = []
	prices = []

	# Regular expression to match key-value pairs
	key_value_pattern = re.compile(r'(\w+): ([\w\.\d]+)')

	# Process each item
	for item in items:
		# Remove leading/trailing braces for the first and last item in the list
		item = item.strip('{}')

		# Extract all key-value pairs
		fields = key_value_pattern.findall(item)

		# Convert to dictionary to access by key
		item_dict = {kv[0]: kv[1] for kv in fields}

		# Append the values to the respective lists
		names.append(item_dict.get('name', ''))
		prices.append(item_dict.get('price', ''))

	# Join the list into a newline-separated string
	names_str = '\n'.join(names)
	prices_str = '\n'.join(prices)

	return names_str, prices_str

def extract_line_items(df, column):
	# Apply the parsing function to the line_items column
	df['line_items.names'], df['line_items.prices'] = zip(*df[column].apply(parse_line_item_string))

	# Optionally, drop the original column if no longer needed
	df.drop(columns=[column], inplace=True)

	return df

def cleanCsv(pathIn, pathOut):
	df = pd.read_csv(pathIn)

	for col in df.columns:
		if df[col].dtype == object:
			df[col] = df[col].apply(remove_brackets)
			df[col] = df[col].apply(make_lists_normal)

	df = keep_defined_headers(df, shopify_defined_headers)

	df = split_columns(df, 'discount_codes', ['code', 'amount'])
	df = split_columns(df, 'customer', ['id', 'email', 'first_name', 'last_name'])
	# df = nested_list(df, 'line_items', ['name', 'price'])
	df = extract_line_items(df, 'line_items')

	df = clear_empty_columns(df)
	df.to_csv(pathOut, index=False)

	print("cleaned csv")