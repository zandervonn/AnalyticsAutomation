import os
import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib import flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, Dimension, Metric, DateRange, OrderBy


def get_credentials(client_secret_path, token_path):

	creds = None
	scopes = ["https://www.googleapis.com/auth/analytics.readonly"]

	# Search for valid credentials
	if os.path.exists(token_path):
		creds = Credentials.from_authorized_user_file(token_path, scopes)

	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			# todo fix if token cannot be refreshed, delete token and go through 2fa
			creds.refresh(Request())
		else:
			appflow = flow.InstalledAppFlow.from_client_secrets_file(
				client_secret_path,
				scopes=scopes,
			)
			launch_browser = True
			if launch_browser:
				creds = appflow.run_local_server()
			else:
				appflow.run_console()
		# Save the credentials for the next run
		with open(token_path, 'w') as token:
			token.write(creds.to_json())
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

	# Initialize the Analytics Data API client
	client = BetaAnalyticsDataClient(credentials=credentials)

	# Dictionary to store the DataFrames for each dimension
	dfs = {}

	# Iterate over each dimension in the Google-defined list
	for dimension in dimensions:
		# Filter the compatibility DataFrame for the current dimension
		compatible_metrics = compatibility_df[compatibility_df['Dimension'] == dimension]['Metric'].tolist()

		# Keep only metrics that are in the Google-defined list
		compatible_metrics = [metric for metric in compatible_metrics if metric in metrics]

		# Split metrics into chunks of 10 due to API limitation
		metric_chunks = [compatible_metrics[i:i + 10] for i in range(0, len(compatible_metrics), 10)]

		# Initialize an empty DataFrame to store results
		results_df = pd.DataFrame()

		# Fetch data for each chunk of metrics
		for metrics in metric_chunks:
			# noinspection PyTypeChecker
			request = RunReportRequest(
				property=f"properties/{property_id}",
				dimensions=[Dimension(name=dimension)],
				metrics=[Metric(name=metric) for metric in metrics],
				date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
				order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name=dimension))]
			)
			response = client.run_report(request)
			chunk_df = build_dataframe(response)
			results_df = pd.concat([results_df, chunk_df], axis=1)

		# Add the results DataFrame to the dictionary
		dfs[dimension] = results_df

	return dfs
