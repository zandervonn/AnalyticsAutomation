import os
from gitignore import access

def path_gen(*args):
	# Define allowed options for each parameter
	allowed_platforms = {'shopify', 'cin7', 'starshipit', 'google', 'facebook', 'instagram', 'compiled'}
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
		raise ValueError("Invalid number of arguments. Expected 1 or 4.")

	# Ensure the subfolder exists
	os.makedirs(subfolder_path, exist_ok=True)

	# Construct the full file path
	file_path = os.path.join(subfolder_path, file_name)

	return file_path