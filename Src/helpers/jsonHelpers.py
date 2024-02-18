import csv
import json
from io import StringIO


def parse_json(text):
	try:
		return json.loads(text)
	except json.JSONDecodeError as e:
		print(f"Error decoding JSON: {e}")
		return None  # or return {}, depending on how you want to handle errors

def json_to_csv(json_data):
	# Check if the JSON data is empty
	if not json_data:
		return ""

	# Determine the headers from the first item in the JSON data
	headers = json_data[0].keys()

	# Create a StringIO object to write the CSV data
	output = StringIO()
	writer = csv.DictWriter(output, fieldnames=headers)

	# Write the headers and data rows
	writer.writeheader()
	for row in json_data:
		writer.writerow(row)

	# Get the CSV string from the StringIO object
	csv_string = output.getvalue()
	output.close()

	return csv_string