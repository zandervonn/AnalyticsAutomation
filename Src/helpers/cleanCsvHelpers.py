# from Src.helpers.jsonHelpers import *
# import numpy as np
# import pandas as pd
# from dateutil import parser
# import pytz
#
# # Define cleaning functions
# def remove_brackets(text):
# 	if isinstance(text, str):
# 		return text.replace("(", "").replace(")", "")
# 	return text
#
# def clean_string_list_column(df, column_name):
# 	if column_name in df.columns:
# 		df[column_name] = df[column_name].apply(
# 			lambda x: ', '.join(str(item) for item in x) if isinstance(x, list) else x)
# 	return df
#
# def make_lists_normal(text):
# 	if isinstance(text, str):
# 		return text.replace("[", "").replace("]", "").replace("'", "")
# 	return text
#
# def clear_empty_columns(df):
# 	df = df.replace('', np.nan)
# 	df = df.dropna(axis=1, how='all')
# 	return df.convert_dtypes()
#
# def round_numeric_columns(df):
# 	for col in df.columns:
# 		if df[col].dtype == object:
# 			try:
# 				df[col] = df[col].astype(float).round(2)
# 			except (ValueError, TypeError):
# 				pass
# 	return df
#
# def standardize_time_format(df, column_name, output_format='%d/%m/%y %I:%M%p'):
# 	if column_name in df.columns:
# 		def safe_parse_date(x):
# 			try:
# 				return parser.parse(x).astimezone(pytz.timezone('UTC')).strftime(output_format)
# 			except (ValueError, TypeError):
# 				return None
#
# 		df[column_name] = df[column_name].apply(safe_parse_date)
# 	return df
#
# def split_list_columns(df, column, keys):
# 	for key in keys:
# 		df[f"{column}.{key}"] = None
#
# 	for index, row in df.iterrows():
# 		items = parse_json(row[column]) if pd.notna(row[column]) else []
# 		if isinstance(items, list) and all(isinstance(item, dict) for item in items):
# 			for key in keys:
# 				df.at[index, f"{column}.{key}"] = "\n".join(str(item.get(key, '')) for item in items)
#
# 	df.drop(columns=[column], inplace=True)
# 	return df
#
# def extract_split_columns_info(defined_headers):
# 	split_columns_info = {}
# 	for header in defined_headers:
# 		if '.' in header:
# 			main_column, subfield = header.split('.', 1)
# 			if main_column not in split_columns_info:
# 				split_columns_info[main_column] = []
# 			split_columns_info[main_column].append(subfield)
# 	return split_columns_info
#
# def apply_splitting(df, split_columns_info):
# 	for main_column, subfields in split_columns_info.items():
# 		if main_column in df.columns:
# 			df = split_list_columns(df, main_column, subfields)
# 	return df
#
# def normalize_object_columns(df):
# 	for col in df.columns:
# 		if df[col].dtype == object:
# 			df[col] = df[col].apply(remove_brackets)
# 			df[col] = df[col].apply(make_lists_normal)
# 			df = clean_string_list_column(df, col)
# 	return df
#
# def clean_date_columns(df):
# 	for col in df.columns:
# 		if 'date' in col.lower():
# 			df = standardize_time_format(df, col)
# 	return df
#
# def reorder_columns(df, defined_headers):
# 	return df[[header for header in defined_headers if header in df.columns]]
#
# def clean_df(df, defined_headers):
# 	split_columns_info = extract_split_columns_info(defined_headers)
# 	df = apply_splitting(df, split_columns_info)
# 	df = normalize_object_columns(df)
# 	df = clean_date_columns(df)
# 	df = clear_empty_columns(df)
# 	df = round_numeric_columns(df)
# 	df = reorder_columns(df, defined_headers)
# 	return df
#
# def clean_dfs(df_dict, headers):
# 	clean_dfs = {}
# 	for dimension, df in df_dict.items():
# 		cleaned_df = clean_df(df, headers)
# 		clean_dfs[dimension] = cleaned_df
# 	return clean_dfs