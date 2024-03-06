from Src.helpers.jsonHelpers import *
import numpy as np
import pandas as pd
from dateutil import parser
import pytz

# Define cleaning functions
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
	for col in df.columns:
		if df[col].dtype == object:
			# Check if the column contains only numeric values
			is_numeric_column = all(
				all(item.replace('.', '', 1).isdigit() for item in line.split('\n') if item)
				for cell in df[col] if isinstance(cell, str)
				for line in cell.split('\n')
			)
			if is_numeric_column:
				try:
					df[col] = df[col].apply(lambda x: '\n'.join(str(round(float(line), 2)) for line in x.split('\n') if line) if isinstance(x, str) else x)
				except (ValueError, TypeError):
					pass
		elif df[col].dtype == float:
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
	for col in df.columns:
		if df[col].dtype == object:
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

def clean_dfs(df_dict, headers):
	clean_dfs = {}
	for dimension, df in df_dict.items():
		cleaned_df = clean_df(df, headers)
		clean_dfs[dimension] = cleaned_df
	return clean_dfs