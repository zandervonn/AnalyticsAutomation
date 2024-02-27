
from google.auth.transport.requests import Request
from google_auth_oauthlib import flow
from google.oauth2.credentials import Credentials
from google.analytics.data import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
	DateRange,
	Dimension,
	Metric,
	OrderBy,
	RunReportRequest
)
import os
import pandas as pd

def get_credentials(client_secret_path, token_path):

	creds = None
	scopes = ["https://www.googleapis.com/auth/analytics.readonly"]

	# Search for valid credentials
	if os.path.exists(token_path):
		creds = Credentials.from_authorized_user_file(token_path, scopes)

	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
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
	#todo check that the values coming back look correct, not lining up with analytics
	#todo clean the date cloumn
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

import requests

import requests
import json

def check_compatibility(credentials, property_id, metrics, dimensions):
	url = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:checkCompatibility"
	headers = {
		"Authorization": f"Bearer {credentials.token}",
		"Content-Type": "application/json"
	}
	payload = {
		"dimensions": [{"name": dim} for dim in dimensions],
		"metrics": [{"name": metric} for metric in metrics]
	}
	response = requests.post(url, headers=headers, data=json.dumps(payload))
	return response.json()

import requests
import json

def check_compatibility(credentials, property_id, metrics, dimensions):
	url = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:checkCompatibility"
	headers = {
		"Authorization": f"Bearer {credentials.token}",
		"Content-Type": "application/json"
	}
	payload = {
		"dimensions": [{"name": dim} for dim in dimensions],
		"metrics": [{"name": metric} for metric in metrics]
	}
	response = requests.post(url, headers=headers, data=json.dumps(payload))

	# Convert response content to JSON and print
	response_json = response.json()
	print(json.dumps(response_json, indent=4))