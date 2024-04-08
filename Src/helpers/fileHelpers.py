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

