import json
import numpy as np
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)

# Define cleaning functions
def remove_brackets(text):
	if isinstance(text, str):  # Ensure the text is a string
		text = text.replace("(", "").replace(")", "")
	return text

def clean_string_list_column(df, column_name):
	if column_name in df.columns:
		df[column_name] = df[column_name].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
	return df

def make_lists_normal(text):
	if isinstance(text, str):  # Ensure the text is a string
		return text.replace("[", "").replace("]", "").replace("'", "")
	return text

def clear_empty_columns(df):
	return df.replace('', np.nan).dropna(axis=1, how='all').infer_objects()

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

	# Iterate over each row and process the data in the specified column
	for index, row in df.iterrows():
		# Check if the data is already a dictionary or a list of dictionaries
		if isinstance(row[column], dict):
			items = [row[column]]  # Wrap the dictionary in a list
		elif isinstance(row[column], list):
			items = row[column]
		else:
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

def clean_df(df, defined_headers):
	# Extract main columns and subfields from defined headers
	split_columns_info = {}
	for header in defined_headers:
		if '.' in header:
			main_column, subfield = header.split('.', 1)
			if main_column not in split_columns_info:
				split_columns_info[main_column] = []
			split_columns_info[main_column].append(subfield)

	# Apply splitting to each column that needs to be split
	for main_column, subfields in split_columns_info.items():
		if main_column in df.columns:
			df = split_columns(df, main_column, subfields)

	# Clean and normalize object columns
	for col in df.columns:
		if df[col].dtype == object:
			# df[col] = df[col].apply(clean_list_like_strings)
			df[col] = df[col].apply(remove_brackets)
			df[col] = df[col].apply(make_lists_normal)
			df = clean_string_list_column(df, col)

	# Clear empty columns
	df = clear_empty_columns(df)

	# Keep only the columns defined in defined_headers
	# Reorder the columns to match the list of defined headers
	df = df[[header for header in defined_headers if header in df.columns]]

	return df
