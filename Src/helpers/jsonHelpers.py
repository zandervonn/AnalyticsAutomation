import csv
import json
from io import StringIO


def parse_json(text):
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

	# Determine the headers from the first item in the data
	headers = data[0].keys()

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