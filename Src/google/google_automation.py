import os
from datetime import datetime

import numpy as np
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, Dimension, Metric, DateRange, OrderBy
from google_auth_oauthlib.flow import InstalledAppFlow

from Src.helpers.clean_csv_helpers import clean_and_convert_date_column
from Src.helpers.csv_helpers import save_df_to_csv
from Src.helpers.file_helpers import path_gen


def get_credentials(client_secret_path, token_path):
	creds = None
	scopes = ["https://www.googleapis.com/auth/analytics.readonly"]

	# Search for valid credentials
	if os.path.exists(token_path):
		creds = Credentials.from_authorized_user_file(token_path, scopes)

	# If there are no (valid) credentials available, let the user log in.
	try:
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				appflow = InstalledAppFlow.from_client_secrets_file(
					client_secret_path,
					scopes=scopes,
				)
				creds = appflow.run_local_server(port=0)
			# Save the credentials for the next run
			with open(token_path, 'w') as token:
				token.write(creds.to_json())
	except Exception as e:
		print("Failed to refresh or obtain new token, error:", e)
		# If the refresh or login fails, delete the token file to force reauthentication
		if os.path.exists(token_path):
			os.remove(token_path)
			print(f"Deleted corrupted token file at {token_path}.")
		# Rerun this function to reattempt login
		creds = get_credentials(client_secret_path, token_path)

	return creds

def build_dataframe(response):
	data = []
	for row in response.rows:
		row_data = {}
		for i, dimension_value in enumerate(row.dimension_values):
			row_data[response.dimension_headers[i].name] = dimension_value.value
		for i, metric_value in enumerate(row.metric_values):
			row_data[response.metric_headers[i].name] = metric_value.value
		data.append(row_data)
	return pd.DataFrame(data)

def get_google_analytics(credentials, property_id, dimensions, metrics, start_date, end_date):
	client = BetaAnalyticsDataClient(credentials=credentials)

	# noinspection PyTypeChecker
	request = RunReportRequest(
		property=f"properties/{property_id}",
		dimensions=[Dimension(name=dim) for dim in dimensions],
		metrics=[Metric(name=metric) for metric in metrics],
		date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
		order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name=dimensions[0]))] if dimensions else []
	)
	response = client.run_report(request)
	return build_dataframe(response)

def get_google_analytics_sheets(credentials, property_id, start_date, end_date, dimensions, metrics):
	# Load compatibility CSV
	compatibility_df = pd.read_csv('google/compatible_pairs.csv')

	start_date = convert_to_google_date_format(start_date)
	end_date = convert_to_google_date_format(end_date)

	# Initialize the Analytics Data API client
	client = BetaAnalyticsDataClient(credentials=credentials)

	# Dictionary to store the DataFrames for each dimension
	dfs = {}

	# Iterate over each dimension in the Google-defined list
	for dimension in dimensions:
		print("Getting google sheet for: ", dimension)
		# Filter the compatibility DataFrame for the current dimension
		compatible_metrics = compatibility_df[compatibility_df['Dimension'] == dimension]['Metric'].tolist()

		# Keep only metrics that are in the Google-defined list
		compatible_metrics = [metric for metric in compatible_metrics if metric in metrics]

		# Skip the request if there are no compatible metrics for this dimension
		if not compatible_metrics:
			print(f"No compatible metrics for dimension: {dimension}")
			continue

		# Split metrics into chunks of 10 due to API limitation
		metric_chunks = [compatible_metrics[i:i + 10] for i in range(0, len(compatible_metrics), 10)]

		# Initialize an empty DataFrame to store results
		results_df = pd.DataFrame()

		# Fetch data for each chunk of metrics
		for metric_chunk in metric_chunks:
			try:
				# noinspection PyTypeChecker
				request = RunReportRequest(
					property=f"properties/{property_id}",
					dimensions=[Dimension(name=dimension)],
					metrics=[Metric(name=metric) for metric in metric_chunk],
					date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
					order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name=dimension))]
				)
				response = client.run_report(request)
				chunk_df = build_dataframe(response)

				if results_df.empty:
					results_df = chunk_df
				else:
					# Merge the chunk_df with the results_df on the dimension column
					results_df = results_df.merge(chunk_df, on=dimension, how='outer')
			except Exception as e:
				print(f"Warning: Failed to fetch data for dimension '{dimension}' and metrics '{metric_chunk}'. Error: {e}")

		# Add the results DataFrame to the dictionary
		dfs[dimension] = results_df

	return dfs

def convert_to_google_date_format(date_str):
	# Parse the date string to a datetime object
	date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
	# Format the date to YYYY-MM-DD
	return date_obj.strftime("%Y-%m-%d")


def clean_google_dfs(google_dfs):
	cleaned_google_dfs = {}
	for dimension, df in google_dfs.items():

		# Check if 'sessionSource' column exists and clean it
		if 'sessionSource' in df.columns:
			df = clean_session_sources(df)

		# Clean and convert date columns
		df = clean_and_convert_date_column(df, 'dateHour', '%Y%m%d%H', '%Y-%m-%d %H:%M')
		df = clean_and_convert_date_column(df, 'date', '%Y%m%d', '%Y-%m-%d')

		cleaned_google_dfs[dimension] = df
	return cleaned_google_dfs

def load_mapping_from_file(file_path):
	"""
	Load mapping from a text file with format:
	<key> = <val>, <val>
	Returns a dictionary where each <val> points to <key>.
	"""
	mapping = {}
	with open(file_path, 'r') as file:
		for line in file:
			key, values = line.strip().split(' = ')
			for value in values.split(', '):
				mapping[value] = key
	return mapping

def clean_session_sources(df):
	"""
	Normalize session sources to consolidate variations by extracting the main part of the domain.
	Then, use a mapping file to correct common variations and aggregate the cleaned data.
	"""
	# Normalize session sources by extracting the main part of the domain
	df['sessionSource'] = df['sessionSource'].apply(
		lambda x: x.split('.')[-2] if '.' in x else x
	)

	for col in df.columns[1:]:
		df[col] = pd.to_numeric(df[col], errors='coerce')

	# Load common variations mapping from a file
	common_mappings = load_mapping_from_file(r"/Users/Zander/Downloads/Automation-Gel 2/config/google/googleSessionsMapping")

	# Replace session sources using the loaded mapping
	df['sessionSource'] = df['sessionSource'].replace(common_mappings)

	# Aggregate the data based on the normalized session sources
	df = aggregate_session_source_data(df)

	return df

def aggregate_session_source_data(df):
	"""
	Aggregate data based on the normalized session source, applying specific aggregation rules.
	Handles cases where weights sum to zero by defaulting to zero and printing debug information.
	Custom aggregations are applied only if the column exists in the DataFrame.
	"""
	# Define a safe weighted average function
	def safe_weighted_average(data, weights):
		if np.sum(weights) == 0:
			print(f"Debug: Zero weights encountered for data: {data.name} with weights: {weights.name}")
			return 0
		return np.average(data, weights=weights)

	# Initialize aggregation rules, defaulting to 'sum' for all columns except 'sessionSource'
	aggregation_rules = {col: 'sum' for col in df.columns if col != 'sessionSource'}

	# Define custom aggregation rules
	custom_aggregations = {
		'advertiserAdCostPerClick': ('advertiserAdClicks', safe_weighted_average),
		'advertiserAdCostPerConversion': ('transactions', safe_weighted_average),
		'averagePurchaseRevenue': ('transactions', safe_weighted_average),
		'averageSessionDuration': ('sessions', safe_weighted_average),
		'returnOnAdSpend': ('advertiserAdCost', safe_weighted_average)
	}

	# # Apply custom aggregations only if the column exists in the DataFrame
	# for key, (weight_col, func) in custom_aggregations.items():
	# 	if key in aggregation_rules and weight_col in df.columns:
	# 		aggregation_rules[key] = lambda x, func=func, weight_col=weight_col: func(x, df.loc[x.index, weight_col])

	# Aggregate the DataFrame
	aggregated_df = df.groupby('sessionSource').agg(aggregation_rules).reset_index()

	return aggregated_df
