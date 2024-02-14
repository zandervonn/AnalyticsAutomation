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

def parse_json(text):
	try:
		return json.loads(text)
	except json.JSONDecodeError as e:
		print(f"Error decoding JSON: {e}")
		return None  # or return {}, depending on how you want to handle errors

def split_columns(df, column, keys):
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
	df = split_columns(df, 'line_items', ['id', 'name', 'price'])
	df = split_columns(df, 'fulfillments', ['id','created_at'])

	for col in df.columns:
		if df[col].dtype == object:
			df[col] = df[col].apply(remove_brackets)
			df[col] = df[col].apply(make_lists_normal)

	df = clear_empty_columns(df)
	df.to_csv(pathOut, index=False)

	print("cleaned csv")