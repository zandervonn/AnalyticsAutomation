import os
from datetime import datetime

import openpyxl
import pandas as pd
import re

from bs4 import BeautifulSoup


def path_gen(*args):

	# Lazy import of output_folder_path
	from Src.access import output_folder_path

	if len(args) == 3:
		platform, data_type, file_format = args

		# Create the subfolder path based on the platform and data type
		subfolder_path = os.path.join(output_folder_path(), platform, data_type)

		file_name = f"{platform}_{data_type}.{file_format}"

	elif len(args) == 1:
		platform, = args

		# Create the subfolder path based on the platform
		subfolder_path = os.path.join(output_folder_path(), 'output', platform)

		# Construct the file name
		file_name = f"{platform}_output.xlsx"

	else:
		raise ValueError("Invalid number of arguments. Expected 1 or 3.")

	# Ensure the subfolder exists
	os.makedirs(subfolder_path, exist_ok=True)

	# Construct the full file path
	file_path = os.path.join(subfolder_path, file_name)

	return file_path

def find_path_upwards(target_relative_path, start_path=None):
	"""
	Searches for a target relative path upwards from the start path until the root is reached.

	:param target_relative_path: The relative path to search for.
	:param start_path: The starting directory for the search. If None, uses the directory of the current file.
	:return: The absolute path to the target if found, None otherwise.
	"""
	if start_path is None:
		start_path = os.path.dirname(__file__)

	current_path = os.path.abspath(start_path)
	root_path = os.path.abspath(os.sep)

	while current_path != root_path:
		potential_target_path = os.path.join(current_path, target_relative_path)
		if os.path.exists(potential_target_path):
			return potential_target_path
		current_path = os.path.dirname(current_path)

	return None

def get_header_list(list_name):
	excel_file_path = find_path_upwards(r'config\headers.xlsx')
	wb = openpyxl.load_workbook(excel_file_path)

	# Get the formatting sheet and the ignore format
	formatting_sheet = wb['formatting']
	ignore_format = formatting_sheet['A1'].fill

	# Get the headers sheet
	headers_sheet = wb['headers']

	for row in headers_sheet.iter_rows():
		if row[0].value == list_name:
			return [cell.value for cell in row[1:] if cell.value and not cell.fill.start_color.index == ignore_format.start_color.rgb]
	return []

def load_mapping(file_path):
	mapping = {}
	with open(file_path, 'r') as file:
		for line in file:
			parts = line.strip().split('=')
			if len(parts) == 2:
				key, value = parts[0].strip(), parts[1].strip()
				mapping[key] = value
	return mapping

def remove_html_tags(text):
	# Remove HTML tags
	text = BeautifulSoup(text, "html.parser").get_text()
	# Remove non-printable characters
	text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
	return text

def read_and_clean_data(file_path):
	try:
		file_extension = os.path.splitext(file_path)[1].lower()
		if file_extension == '.csv':
			df = pd.read_csv(file_path)
		elif file_extension in ['.xls', '.xlsx']:
			df = pd.read_excel(file_path)
		else:
			print(f"Unsupported file type: {file_path}")
			return None
		# Remove HTML tags from string columns
		df = df.applymap(lambda x: remove_html_tags(x) if isinstance(x, str) else x)
		return df
	except Exception as e:
		print(f"Error processing {file_path}: {e}")
		return None

def save_data_to_excel(df, writer, sheet_name):
	if df is not None:
		df.to_excel(writer, sheet_name=sheet_name, index=False)

def create_date_saved_df(all_data_columns):
	date_saved = 'Date Saved: ' + datetime.now().strftime('%Y-%m-%d')
	return pd.DataFrame([[date_saved] + [''] * (all_data_columns - 1)])

def files_to_excel(file_paths, output_excel_path):
	with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
		for file_path in file_paths:
			df = read_and_clean_data(file_path)
			if df is not None:
				sheet_name = os.path.basename(file_path).split('.')[0][:31]  # Excel sheet name limit
				save_data_to_excel(df, writer, sheet_name)

	print(f"Files saved to {output_excel_path}")


def update_template_files(template_folder, data_folder, output_folder):
	# Load available data files into a dictionary
	data_files = get_excel_csv_files(data_folder)
	data_dict = load_files_into_dict(data_files)
	print("Data dictionary keys:", list(data_dict.keys()))  # Debug: Print available keys

	# Load template files
	template_files = get_excel_csv_files(template_folder)

	# Create a subfolder in the output directory with today's date
	today = datetime.now().strftime("%Y-%m-%d")
	date_output_folder = os.path.join(output_folder, today)
	if not os.path.exists(date_output_folder):
		os.makedirs(date_output_folder)

	for template_file in template_files:
		wb = openpyxl.load_workbook(template_file)
		for sheet_name in wb.sheetnames:
			ws = wb[sheet_name]
			header = ws[2]  # Assume second row contains references

			for col, cell in enumerate(header, start=1):
				ref = str(cell.value).strip().lower() if cell.value else ""
				if not ref or '.' not in ref:
					continue  # Skip cells without proper references

				update_header = ref.endswith('_headers')
				ref = ref[:-8] if update_header else ref  # Remove '_headers' suffix if present

				parts = [x.strip() for x in ref.split('.')]
				if len(parts) < 3:
					print(f"Reference in cell {cell.coordinate} is incomplete: '{cell.value}'")
					continue

				file, sheet, column = parts
				key = f"{file}.{sheet}".lower()

				if key not in data_dict:
					print(f"Could not find data for key: '{key}'")
					continue

				df = data_dict[key]
				if column == "all":
					replace_entire_sheet(ws, df, col, update_header)
				elif column in df.columns:
					replace_column_data(ws, col, df[column], update_header)
				else:
					print(f"Column '{column}' not found in data for key: '{key}'")

			ws.delete_rows(2)  # Remove the reference row

		# Construct the full output path including the date subfolder
		file_name, file_extension = os.path.splitext(os.path.basename(template_file))
		output_path = os.path.join(date_output_folder, f"{file_name}_{today}{file_extension}")
		wb.save(output_path)
		print(f"Saved processed file to: {output_path}")

def replace_entire_sheet(ws, df, start_col, update_header):
	# Assuming row 1 is headers and row 2 is the reference row
	data_start_row = 2 if update_header else 3

	# Clear data from the columns to be updated
	for col in range(start_col, start_col + len(df.columns)):
		for row in range(data_start_row, ws.max_row + 1):
			ws.cell(row=row, column=col).value = None

	# Insert new data
	for idx, (i, row) in enumerate(df.iterrows(), start=data_start_row):
		for j, value in enumerate(row, start=start_col):
			ws.cell(row=idx, column=j).value = value

	# Update headers if required
	if update_header:
		for i, col_name in enumerate(df.columns, start=start_col):
			ws.cell(row=1, column=i).value = col_name

def replace_column_data(ws, col, data, update_header):
	data_start_row = 2 if update_header else 3
	max_row = max(data_start_row, ws.max_row)
	for row in range(data_start_row, max_row + 1):
		ws.cell(row=row, column=col).value = None
	for i, value in enumerate(data, start=data_start_row):
		ws.cell(row=i, column=col, value=value)
	if update_header:
		ws.cell(row=1, column=col, value=data.name)

def indicate_missing(ws, row, col, file, sheet, column=None):
	if column:
		message = f"MISSING {file}.{sheet}.{column}"
	else:
		message = f"MISSING {file}.{sheet}"
	ws.cell(row=row, column=col, value=message)

def load_files_into_dict(files):
	"""
	Load multiple data files (Excel and CSV) into a dictionary of DataFrames.
	Keys are formatted as 'filename.sheetname' for Excel files and 'filename.filename' for CSV files.
	"""
	data_dict = {}
	for file in files:
		file_name, file_ext = os.path.splitext(file)
		base_file_key = os.path.basename(file_name).lower().strip()

		try:
			if file_ext in ['.xlsx', '.xls']:
				wb = openpyxl.load_workbook(file, data_only=True)
				for sheet in wb.sheetnames:
					df = pd.read_excel(file, sheet_name=sheet)
					df.columns = df.columns.str.strip().str.lower()
					key = f"{base_file_key}.{sheet.lower().strip()}"
					data_dict[key] = df
			elif file_ext == '.csv':
				df = pd.read_csv(file)
				df.columns = df.columns.str.strip().str.lower()
				# For CSV files, assume sheet name is same as file name
				key = f"{base_file_key}.{base_file_key}"
				data_dict[key] = df
		except Exception as e:
			print(f"Error loading file {file}: {e}")
	return data_dict

def get_excel_files_from_folder(folder):
	"""
	Retrieve a list of all Excel files in a folder.

	Parameters:
	- folder (str): Path to the folder to search for Excel files.

	Returns:
	- list: List of paths to the Excel files.
	"""
	excel_files = []
	for root, _, files in os.walk(folder):
		for file in files:
			if file.endswith('.xlsx'):
				excel_files.append(os.path.join(root, file))
	return excel_files

def get_excel_csv_files(folder):
	"""
	Find and print paths of all Excel and CSV files in a folder.

	Parameters:
	- folder (str): Path to the folder to search for Excel and CSV files.

	Returns:
	- list: List of paths to the Excel and CSV files.
	"""
	excel_files = []
	for root, _, files in os.walk(folder):
		for file in files:
			if file.endswith(('.xlsx', '.xls', '.csv')):
				file_path = os.path.join(root, file)
				excel_files.append(file_path)
	return excel_files


def get_all_files(folder):
	"""
	Create a dictionary with file names as keys and full paths as values for all Excel and CSV files in a directory.
	"""
	files_dict = {}
	for root, _, files in os.walk(folder):
		for file in files:
			if file.endswith(('.xlsx', '.xls', '.csv')):
				file_key = file.lower().split('.')[0]
				files_dict[file_key] = os.path.join(root, file)
	return files_dict

def load_data(file_path, sheet_name=None):
	"""
	Load data from an Excel or CSV file into a DataFrame.
	"""
	ext = os.path.splitext(file_path)[1]
	if ext in ['.xlsx', '.xls']:
		return pd.read_excel(file_path, sheet_name=sheet_name)
	elif ext == '.csv':
		return pd.read_csv(file_path)
	else:
		raise ValueError(f"Unsupported file extension: {ext}")