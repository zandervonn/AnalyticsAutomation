import csv
import json
import pandas as pd
from io import StringIO

def dump(json_in):
	tmp = json.dumps(json_in, indent=4)
	print(tmp)

def parse_json(text):
	if isinstance(text, dict):
		return text  # Return the dictionary directly if the input is already a dictionary
	try:
		return json.loads(text)
	except json.JSONDecodeError as e:
		print(f"Error decoding JSON: {e}")
		return None  # or return {}, depending on how you want to handle errors

def save_json(orders, filename):
	with open(filename, 'w', encoding='utf-8') as f:
		json.dump(orders, f, ensure_ascii=False, indent=4)
	print(f"Orders saved to {filename}")

def load_json(orders_path):
	with open(orders_path, 'r', encoding='utf-8') as f:
		orders = json.load(f)
	return orders

def json_to_csv(json_data):
	# Check if the JSON data is empty
	if not json_data:
		return ""

	# Parse the JSON string into a Python object
	data = json.loads(json_data)

	# Dynamically determine the headers by collecting all unique keys from the data
	headers = set()
	for row in data:
		headers.update(row.keys())

	# Sort the headers for consistent column ordering
	headers = sorted(headers)

	# Create a StringIO object to write the CSV data
	output = StringIO()
	writer = csv.DictWriter(output, fieldnames=headers)

	# Write the headers and data rows
	writer.writeheader()
	for row in data:
		writer.writerow(row)

	# Get the CSV string from the StringIO object
	csv_string = output.getvalue()
	output.close()

	return csv_string

def json_to_df(json_data):
	# Check if the JSON data is empty
	if not json_data:
		return pd.DataFrame()

	# Parse the JSON string into a Python object
	data = json.loads(json_data)

	# Convert the data to a pandas DataFrame
	df = pd.DataFrame(data)

	return df

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