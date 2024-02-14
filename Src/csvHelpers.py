import json
import numpy as np
import pandas as pd

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

def parse_json(text):
	try:
		return json.loads(text)
	except json.JSONDecodeError as e:
		print(f"Error decoding JSON: {e}")
		return None  # or return {}, depending on how you want to handle errors

def split_columns_with_json_lists(df, column, keys):
	# Create new columns for each key
	for key in keys:
		df[f"{column}.{key}"] = None

	# Iterate over each row and process the JSON string in the specified column
	for index, row in df.iterrows():
		# Parse the JSON string into a list of dictionaries
		items = parse_json(row[column]) if pd.notna(row[column]) else []

		# Ensure items is a list of dicts
		if isinstance(items, list) and all(isinstance(item, dict) for item in items):
			# Extract values for each key
			for key in keys:
				# Join the values with line breaks and assign to the DataFrame
				df.at[index, f"{column}.{key}"] = "\n".join(str(item.get(key, '')) for item in items)

	# Optionally, drop the original column if no longer needed
	df.drop(columns=[column], inplace=True)

	return df

def cleanCsv(pathIn, pathOut):
	df = pd.read_csv(pathIn)

	df = split_columns(df, 'discount_codes', ['code', 'amount'])
	df = split_columns(df, 'customer', ['id', 'email', 'first_name', 'last_name'])
	df = split_columns_with_json_lists(df, 'line_items', ['id', 'name', 'price'])
	df = split_columns_with_json_lists(df, 'fulfillments', ['id','created_at'])

	for col in df.columns:
		if df[col].dtype == object:
			df[col] = df[col].apply(remove_brackets)
			df[col] = df[col].apply(make_lists_normal)

	df = clear_empty_columns(df)
	df.to_csv(pathOut, index=False)

	print("cleaned csv")