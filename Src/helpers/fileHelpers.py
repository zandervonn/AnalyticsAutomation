import os

import openpyxl
import pandas as pd

from gitignore import access

def path_gen(*args):
	# Define allowed options for each parameter
	allowed_platforms = {'shopify', 'cin7', 'starshipit', 'google', 'facebook', 'facebook_posts', 'facebook_videos', 'instagram', 'instagram_posts', 'compiled'}
	allowed_data_types = {'orders', 'customers', 'conversions', 'sessions', 'data'}
	allowed_file_formats = {'json', 'csv', 'xlsx'}

	if len(args) == 3:
		platform, data_type, file_format = args

		# Check that the provided arguments are valid
		if platform not in allowed_platforms:
			raise ValueError(f"Invalid platform: {platform}. Allowed options: {allowed_platforms}")
		if data_type not in allowed_data_types:
			raise ValueError(f"Invalid data type: {data_type}. Allowed options: {allowed_data_types}")
		if file_format not in allowed_file_formats:
			raise ValueError(f"Invalid file format: {file_format}. Allowed options: {allowed_file_formats}")

		# Create the subfolder path based on the platform and data type
		subfolder_path = os.path.join(access.FOLDER_PATH, platform, data_type)

		file_name = f"{platform}_{data_type}.{file_format}"

	elif len(args) == 1:
		platform, = args

		# Check that the provided argument is valid
		if platform not in allowed_platforms:
			raise ValueError(f"Invalid platform: {platform}. Allowed options: {allowed_platforms}")

		# Create the subfolder path based on the platform
		subfolder_path = os.path.join(access.FOLDER_PATH, 'output', platform)

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

def files_to_excel(file_paths, output_excel_path):
	with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
		for file_path in file_paths:
			file_extension = os.path.splitext(file_path)[1].lower()
			if file_extension == '.csv':
				try:
					df = pd.read_csv(file_path)
					sheet_name = os.path.basename(file_path).split('.')[0]
					sheet_name = sheet_name[:31]  # Excel sheet name limit
					df.to_excel(writer, sheet_name=sheet_name, index=False)
				except pd.errors.EmptyDataError:
					print(f"Warning: {file_path} is empty and was skipped.")
			elif file_extension in ['.xls', '.xlsx']:
				try:
					xls = pd.ExcelFile(file_path)
					for sheet_name in xls.sheet_names:
						df = pd.read_excel(file_path, sheet_name=sheet_name)
						sheet_name = sheet_name[:31]  # Excel sheet name limit
						df.to_excel(writer, sheet_name=sheet_name, index=False)
				except Exception as e:
					print(f"Error reading {file_path}: {e}")
			else:
				print(f"Unsupported file type: {file_path}")

	print(f"Files saved to {output_excel_path}")