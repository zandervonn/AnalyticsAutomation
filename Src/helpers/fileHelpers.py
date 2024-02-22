import os
from Src.gitignore import access


def path_gen(platform, data_type, clean_status, file_format):
	# Define allowed options for each parameter
	allowed_platforms = {'shopify', 'cin7', 'starshipit', 'google'}
	allowed_data_types = {'orders', 'customers', 'conversions', 'sessions'}
	allowed_clean_statuses = {'clean', ''}
	allowed_file_formats = {'json', 'csv'}

	# Check that the provided arguments are valid
	if platform not in allowed_platforms:
		raise ValueError(f"Invalid platform: {platform}. Allowed options: {allowed_platforms}")
	if data_type not in allowed_data_types:
		raise ValueError(f"Invalid data type: {data_type}. Allowed options: {allowed_data_types}")
	if clean_status not in allowed_clean_statuses:
		raise ValueError(f"Invalid clean status: {clean_status}. Allowed options: {allowed_clean_statuses}")
	if file_format not in allowed_file_formats:
		raise ValueError(f"Invalid file format: {file_format}. Allowed options: {allowed_file_formats}")

	# Create the subfolder path based on the platform and data type
	subfolder_path = os.path.join(access.FOLDER_PATH, platform, data_type)

	# Ensure the subfolder exists
	os.makedirs(subfolder_path, exist_ok=True)

	# Construct the file name
	file_name = ""
	if clean_status:
		file_name += f"{clean_status}_"
	file_name += f"{platform}_{data_type}.{file_format}"

	# Construct the full file path
	file_path = os.path.join(subfolder_path, file_name)

	return file_path