import pandas as pd
import numpy as np
import json
import re

# Define cleaning functions that operate on strings
def remove_brackets(text):
	if isinstance(text, str):  # Ensure the text is a string
		return text.replace("(", "").replace(")", "")
	return text

def make_lists_normal(text):
	if isinstance(text, str):  # Ensure the text is a string
		return text.replace("[", "").replace("]", "").replace("'", "")
	return text

def clear_empty_columns(df):
	return df.replace('', np.nan).dropna(axis=1, how='all')

def parse_cell_to_text(cell):
	if pd.isna(cell) or not isinstance(cell, str):
		return cell  # Return as-is if the cell is NaN or not a string

	# Convert single quotes to double quotes and remove unwanted characters
	# to make the string JSON compatible.
	cell_json_compatible = re.sub(r"\b(\w+): '([^']+)'", r'"\1": "\2"', cell)
	cell_json_compatible = cell_json_compatible.replace("'", '"').replace("{", '{"').replace(": ", '": ').replace(", ", ', "').replace("}", '"}')

	try:
		# Try to parse the string as a dictionary
		cell_dict = json.loads(cell_json_compatible)

		# If parsing is successful and 'shop_money' is a key, format the amount and currency code
		if isinstance(cell_dict, dict) and 'shop_money' in cell_dict:
			amount = cell_dict['shop_money'].get('amount', 0)
			currency_code = cell_dict['shop_money'].get('currency_code', '')
			return f"{amount} {currency_code}"
		else:
			# Handle other dictionary-like strings here, if necessary
			pass
	except json.JSONDecodeError:
		# The string is not a valid JSON, handle it as a list-like string
		pass

	# If the cell contains a list of dictionaries (as indicated by curly braces),
	# extract key-value pairs into a readable string.
	if "{" in cell and "}" in cell:
		pairs = re.findall(r"{([^}]+)}", cell)
		cleaned_pairs = []
		for pair in pairs:
			# Split the pair on the first colon only
			key, value = pair.split(": ", 1)
			cleaned_pairs.append(f"{key.strip()}: {value.strip()}")
		return '; '.join(cleaned_pairs)

	# If the cell content couldn't be parsed, return it as is
	return cell

def cleanCsv(pathIn, pathOut):
	# Load the CSV data into a DataFrame
	df = pd.read_csv(pathIn)

	# Apply cleaning functions column-wise where applicable
	for col in df.columns:
		if df[col].dtype == object:  # Apply only to columns with object datatype
			df[col] = df[col].apply(remove_brackets)
			df[col] = df[col].apply(make_lists_normal)
			# df[col] = df[col].apply(parse_cell_to_text)

	df = clear_empty_columns(df)

	# Save the cleaned DataFrame to a new CSV
	df.to_csv(pathOut, index=False)