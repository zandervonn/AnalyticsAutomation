import csv
from collections import defaultdict

from google.api_core.exceptions import InvalidArgument, InternalServerError
from google.analytics.data import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
	RunReportRequest
)

def get_compatible_metrics(credentials, property_id, dimensions, metrics, output_file="Src/google/compatible_pairs.csv"):
	client = BetaAnalyticsDataClient(credentials=credentials)
	compatible_pairs = []

	with open(output_file, "w", newline="") as file:
		writer = csv.writer(file)
		writer.writerow(["Dimension", "Metric"])

		for i, dimension in enumerate(dimensions):
			for j, metric in enumerate(metrics):
				print(f"Checking compatibility: Dimension {i + 1}/{len(dimensions)}, Metric {j + 1}/{len(metrics)}")
				try:
					# noinspection PyTypeChecker
					request = RunReportRequest(
						property=f"properties/{property_id}",
						dimensions=[{"name": dimension}],
						metrics=[{"name": metric}],
						date_ranges=[{"start_date": "2023-01-01", "end_date": "2023-01-02"}]  # Use a short date range for testing
					)
					client.run_report(request)
					compatible_pairs.append((dimension, metric))
					writer.writerow([dimension, metric])
					print(f"Compatible: {dimension}, {metric}")
				except InvalidArgument:
					print(f"Incompatible: {dimension}, {metric}")
				except InternalServerError:
					print("Internal server error, skipping this pair")
					continue

	return compatible_pairs

def invert_compatible_pairs(compatible_pairs):
	dimension_metrics_map = defaultdict(list)
	for dimension, metric in compatible_pairs:
		dimension_metrics_map[dimension].append(metric)
	return dict(dimension_metrics_map)

import csv

def convert_to_table(input_file="compatible_pairs.csv", output_file="compatibility_matrix.csv"):
	# Read the compatible pairs from the input file
	with open(input_file, "r") as file:
		reader = csv.reader(file)
		next(reader)  # Skip the header row
		compatible_pairs = [(row[0], row[1]) for row in reader]

	# Extract unique dimensions and metrics
	dimensions = sorted(set(pair[0] for pair in compatible_pairs))
	metrics = sorted(set(pair[1] for pair in compatible_pairs))

	# Create a compatibility matrix
	compatibility_matrix = [["Dimension"] + metrics]
	for dimension in dimensions:
		row = [dimension] + ["x" if (dimension, metric) in compatible_pairs else "" for metric in metrics]
		compatibility_matrix.append(row)

	# Write the compatibility matrix to the output file
	with open(output_file, "w", newline="") as file:
		writer = csv.writer(file)
		writer.writerows(compatibility_matrix)

	print(f"Compatibility matrix saved to {output_file}")