import os
from Src.helpers.jsonHelpers import *
from dateutil import parser
import numpy as np
import pandas as pd

# todo move
import pytz

webdriver_path = 'C:\\Users\\Zander\\.wdm\\chromedriver\\72.0.3626.7\\win32\\chromedriver.exe'
target_url = 'https://google.com'

def standardize_time_format(df, column_name, output_format='%d/%m/%y %I:%M%p'):
	if column_name in df.columns:
		def safe_parse_date(x):
			try:
				return parser.parse(x).astimezone(pytz.timezone('UTC')).strftime(output_format)
			except (ValueError, TypeError):
				return None  # or return x if you want to keep the original value in case of parsing errors

		df[column_name] = df[column_name].apply(safe_parse_date)
	return df

def split_json_list_columns(df, column, keys):
	# Create new columns for each key
	for key in keys:
		df[f"{column}.{key}"] = None

	# Iterate over each row and process the data in the specified column
	for index, row in df.iterrows():
		# Check if the data is a dictionary or a list of dictionaries
		if isinstance(row[column], dict):
			items = [row[column]]  # Wrap the dictionary in a list
		elif isinstance(row[column], list):
			items = row[column]
		else:
			items = parse_json(row[column]) if pd.notna(row[column]) else []

		# Ensure items is a list of dicts
		if isinstance(items, list) and all(isinstance(item, dict) for item in items):
			# Extract values for each key
			for key in keys:
				# Join the values with line breaks and assign to the DataFrame
				df.at[index, f"{column}.{key}"] = "\n".join(str(item.get(key, '')) for item in items)

	# Optionally, drop the original column if no longer needed
	df.drop(columns=[column], inplace=True)

	return df

def csv_sheets_to_excel(csv_files, excel_file):
	with pd.ExcelWriter(excel_file) as writer:
		for csv_file in csv_files:
			try:
				df = pd.read_csv(csv_file)
			except pd.errors.EmptyDataError:
				df = pd.DataFrame()  # Create an empty DataFrame if the CSV is empty
			# Use only the file name for the sheet name, removing invalid characters
			sheet_name = os.path.basename(csv_file).split('.')[0]
			sheet_name = sheet_name.replace('\\', '_').replace('/', '_').replace('*', '').replace('?', '').replace(':', '').replace('[', '').replace(']', '')
			# Shorten the sheet name to the Excel limit of 31 characters if necessary
			sheet_name = sheet_name[:31]
			df.to_excel(writer, sheet_name=sheet_name, index=False)

def save_to_csv(data, file_name):
	df = pd.DataFrame(data[1:], columns=data[0])
	df.to_csv(file_name, index=False)

def save_df_to_csv(df, file_path):
	df.to_csv(file_path, index=False)
	print(f"CSV saved to {file_path}")

def save_df_to_excel(df_or_dict, filename):
	with pd.ExcelWriter(filename, engine='openpyxl') as writer:
		if isinstance(df_or_dict, pd.DataFrame):
			# If a single DataFrame is provided, save it to the first sheet
			df_or_dict.to_excel(writer, sheet_name='Sheet1', index=False)
		elif isinstance(df_or_dict, dict):
			# If a dictionary of DataFrames is provided, save each DataFrame to a separate sheet
			for sheet_name, df in df_or_dict.items():
				if not isinstance(df, pd.DataFrame):
					raise TypeError(f"The value for key '{sheet_name}' is not a DataFrame. It is of type {type(df)}.")
				if df.empty:
					raise ValueError(f"The DataFrame for key '{sheet_name}' is empty. Cannot create an empty sheet.")
				df.to_excel(writer, sheet_name=sheet_name[:31], index=False)  # Sheet name limited to 31 characters
		else:
			raise TypeError("Input must be a DataFrame or a dictionary of DataFrames.")


def load_csv(path):
	return pd.read_csv(path)

def write_data_to_csv(data, file_path):
	with open(file_path, mode='w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(data.keys())
		writer.writerow(data.values())

def update_files(raw_folder, update_folder):
	# Get all Excel files in the raw folder
	raw_files = [os.path.join(raw_folder, f) for f in os.listdir(raw_folder) if f.endswith('.xlsx')]

	# Load all raw files into a dictionary of DataFrames
	raw_data = {}
	for raw_file in raw_files:
		raw_data[os.path.basename(raw_file)] = pd.read_excel(raw_file, sheet_name=None)

	# Get all Excel files in the update folder
	update_files = [os.path.join(update_folder, f) for f in os.listdir(update_folder) if f.endswith('.xlsx')]

	# Iterate through the files to update
	for update_file in update_files:
		# Load the file to be updated
		writer = pd.ExcelWriter(update_file, engine='openpyxl', mode='a', if_sheet_exists='replace')
		book = writer.book
		for sheet_name in book.sheetnames:
			# Load the sheet
			df = pd.read_excel(update_file, sheet_name=sheet_name)

			# Iterate through the columns in the file to update
			for col in df.columns:
				# Parse the column header to find the corresponding raw file and column
				file, sheet, name = col.split('.')
				if file in raw_data and sheet in raw_data[file]:
					raw_sheet_df = raw_data[file][sheet]
					if name in raw_sheet_df.columns:
						# Update the column with data from the raw file
						df[col] = raw_sheet_df[name]

			# Save the updated DataFrame back to the Excel file
			df.to_excel(writer, sheet_name=sheet_name, index=False)

		# Close the writer to save changes
		writer.close()