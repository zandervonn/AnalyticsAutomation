import os

from Src.helpers.jsonHelpers import *
import csv
import numpy as np
import pandas as pd

# pd.set_option('future.no_silent_downcasting', True)

webdriver_path = 'C:\\Users\\Zander\\.wdm\\chromedriver\\72.0.3626.7\\win32\\chromedriver.exe'
target_url = 'https://google.com'

# Define cleaning functions
def remove_brackets(text):
	if isinstance(text, str):  # Ensure the text is a string
		text = text.replace("(", "").replace(")", "")
	return text

def clean_string_list_column(df, column_name):
	if column_name in df.columns:
		df[column_name] = df[column_name].apply(
			lambda x: ', '.join(str(item) for item in x) if isinstance(x, list) else x)
	return df

def make_lists_normal(text):
	if isinstance(text, str):  # Ensure the text is a string
		return text.replace("[", "").replace("]", "").replace("'", "")
	return text

def clear_empty_columns(df):
	return df.replace('', np.nan).dropna(axis=1, how='all').infer_objects()

def split_json_list_columns(df, column, keys):
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
			df = split_json_list_columns(df, main_column, subfields)

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

def csv_sheets_to_excel(csv_files, excel_file):
	with pd.ExcelWriter(excel_file) as writer:
		for csv_file in csv_files:
			try:
				df = pd.read_csv(csv_file)
			except pd.errors.EmptyDataError:
				df = pd.DataFrame()  # Create an empty DataFrame if the CSV is empty
			# Use only the file name for the sheet name, removing invalid characters
			sheet_name = os.path.basename(csv_file).split('.')[0]
			sheet_name = sheet_name.replace('\\', '_').replace('/', '_').replace('*', '').replace('?', '').replace(':', '').replace('[', '').replace(']', '')
			# Shorten the sheet name to the Excel limit of 31 characters if necessary
			sheet_name = sheet_name[:31]
			df.to_excel(writer, sheet_name=sheet_name, index=False)

def save_to_csv(data, file_name):
	df = pd.DataFrame(data[1:], columns=data[0])
	df.to_csv(file_name, index=False)

def save_df_to_csv(df, file_path):
	df.to_csv(file_path, index=False)
	print(f"CSV saved to {file_path}")

def load_csv(path):
	return pd.read_csv(path)


def write_data_to_csv(data, file_path):
	with open(file_path, mode='w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(data.keys())
		writer.writerow(data.values())

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