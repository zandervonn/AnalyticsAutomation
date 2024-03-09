from datetime import datetime

from Src.helpers.jsonHelpers import *
import numpy as np
import pandas as pd
from dateutil import parser
import pytz

# Define cleaning functions
def clean_and_convert_date_column(df, col, input_format, output_format):
	def convert_date(x):
		if pd.isna(x):
			return None
		else:
			return datetime.strptime(str(x), input_format).strftime(output_format)

	if col in df.columns:
		df[col] = df[col].map(convert_date)
	return df

def remove_brackets(text):
	if isinstance(text, str):
		return text.replace("(", "").replace(")", "")
	return text

def clean_string_list_column(df, column_name):
	if column_name in df.columns:
		df[column_name] = df[column_name].apply(
			lambda x: ', '.join(str(item) for item in x) if isinstance(x, list) else x)
	return df

def make_lists_normal(text):
	if isinstance(text, str):
		return text.replace("[", "").replace("]", "").replace("'", "")
	return text

def clear_empty_columns(df):
	df = df.map(lambda x: np.nan if x == '' else x)
	df = df.dropna(axis=1, how='all')
	return df

def round_numeric_columns(df):
	# Select only columns with dtype 'object'
	object_columns = df.select_dtypes(include=['object']).columns

	# Check and round numeric values in object columns
	for col in object_columns:
		is_float_column = any(
			'.' in item
			for cell in df[col] if isinstance(cell, str)
			for item in cell.split('\n') if item
		)
		if is_float_column:
			try:
				df[col] = df[col].apply(lambda x: '\n'.join(str(round(float(item), 2)) for item in x.split('\n') if item) if isinstance(x, str) else x)
			except (ValueError, TypeError):
				pass

	# Round numeric columns with dtype 'float'
	float_columns = df.select_dtypes(include=['float']).columns
	for col in float_columns:
		df[col] = df[col].round(2)

	return df

def standardize_time_format(df, column_name, output_format='%Y-%m-%dT%H:%M:%S'):
	if column_name in df.columns:
		def safe_parse_date(x):
			try:
				return parser.parse(x).astimezone(pytz.timezone('UTC')).strftime(output_format)
			except (ValueError, TypeError):
				return x  # keep the original value in case of parsing errors

		df[column_name] = df[column_name].apply(safe_parse_date)
	return df

def split_list_columns(df, column, keys):
	for key in keys:
		df[f"{column}.{key}"] = None

	for index, row in df.iterrows():
		items = row[column] if isinstance(row[column], list) else parse_json(row[column]) if pd.notna(row[column]) else []
		if isinstance(items, list) and all(isinstance(item, dict) for item in items):
			for key in keys:
				df.at[index, f"{column}.{key}"] = "\n".join(str(item.get(key, '')) for item in items)

	df.drop(columns=[column], inplace=True)
	return df

def extract_split_columns_info(defined_headers):
	split_columns_info = {}
	for header in defined_headers:
		if '.' in header:
			main_column, subfield = header.split('.', 1)
			if main_column not in split_columns_info:
				split_columns_info[main_column] = []
			split_columns_info[main_column].append(subfield)
	return split_columns_info

def apply_splitting(df, split_columns_info):
	for main_column, subfields in split_columns_info.items():
		if main_column in df.columns:
			df = split_list_columns(df, main_column, subfields)
	return df

def normalize_object_columns(df):
	# Select only columns with dtype 'object'
	object_columns = df.select_dtypes(include=['object']).columns

	# Apply transformations to each object column
	for col in object_columns:
		df[col] = df[col].apply(remove_brackets)
		df[col] = df[col].apply(make_lists_normal)
		df = clean_string_list_column(df, col)

	return df

def reorder_columns(df, defined_headers):
	return df[[header for header in defined_headers if header in df.columns]]

def sort_by_date_column(df, date_column, date_format='%Y-%m-%dT%H:%M:%S%z'):
	# Find the first date column in the DataFrame
	if date_column:
		# Convert the date column to datetime for sorting
		df[date_column] = pd.to_datetime(df[date_column], format=date_format, errors='coerce')
		# Sort by the date column from highest to lowest
		df = df.sort_values(by=date_column, ascending=False)
	return df

def sort_by_value_column(df, column_name, ascending=False):
	return df.sort_values(by=column_name, ascending=ascending)

def clean_df(df, defined_headers):
	split_columns_info = extract_split_columns_info(defined_headers)
	df = apply_splitting(df, split_columns_info)
	df = normalize_object_columns(df)
	df = clear_empty_columns(df)
	df = round_numeric_columns(df)
	df = reorder_columns(df, defined_headers)
	return df

def clean_dfs(df_input, headers):
	if isinstance(df_input, dict):
		clean_dfs = {}
		for dimension, df in df_input.items():
			cleaned_df = clean_df(df, headers)
			clean_dfs[dimension] = cleaned_df
	elif isinstance(df_input, list):
		clean_dfs = []
		for df in df_input:
			cleaned_df = clean_df(df, headers)
			clean_dfs.append(cleaned_df)
	else:
		raise TypeError("Input must be either a list or a dictionary of DataFrames")

	return clean_dfs