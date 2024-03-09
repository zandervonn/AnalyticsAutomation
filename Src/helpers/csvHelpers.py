import os
from Src.helpers.jsonHelpers import *


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
	print(f"CSV saved to {excel_file}")

def save_to_csv(data, file_name):
	df = pd.DataFrame(data[1:], columns=data[0])
	df.to_csv(file_name, index=False)
	print(f"CSV saved to {file_name}")

def save_df_to_csv(df, file_path):
	df.to_csv(file_path, index=False)
	print(f"CSV saved to {file_path}")

def save_df_to_excel(df_or_dict, filename):
	with pd.ExcelWriter(filename, engine='openpyxl') as writer:
		if isinstance(df_or_dict, pd.DataFrame):
			# If a single DataFrame is provided, save it to the first sheet
			if not df_or_dict.empty:
				df_or_dict.to_excel(writer, sheet_name='Sheet1', index=False)
			else:
				print("The input DataFrame is empty. No Excel file created.")
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

	print(f"Excel saved to {filename}")


def load_csv(path):
	try:
		return pd.read_csv(path)
	except Exception as e:
		print(f"Warning: Failed to load {path}. Error: {e}")
		return pd.DataFrame()

def write_data_to_csv(data, file_path):
	with open(file_path, mode='w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(data.keys())
		writer.writerow(data.values())

def get_excel_files_from_folder(folder):
	excel_files = []
	for root, _, files in os.walk(folder):
		for file in files:
			if file.endswith('.xlsx'):
				excel_files.append(os.path.join(root, file))
	return excel_files

def get_excel_files(folder):
	excel_files = []
	for root, _, files in os.walk(folder):
		for file in files:
			if file.endswith('.xlsx'):
				file_path = os.path.join(root, file)
				excel_files.append(file_path)
				print(f"Found Excel file: {file_path}")
	return excel_files

def load_excel_files_into_dict(file_list):
	data_dict = {}
	for file in file_list:
		file_name = os.path.basename(file)
		data_dict[file_name] = pd.read_excel(file, sheet_name=None)
		print(f"Loading file into dictionary: {file} (basename: {file_name})")
	return data_dict

def update_columns(df, raw_data):
	for col in df.columns:
		period_count = col.count('.')
		if period_count >= 2:
			parts = col.split('.', 2)
			file, sheet, name = parts if period_count == 2 else parts[:2] + ['.'.join(parts[2:])]
			file += '.xlsx'  # Add the .xlsx extension to the file name
			print(f"Checking column: {col}")
			if file in raw_data:
				print(f"Found file '{file}' in raw data.")
				if sheet in raw_data[file]:
					print(f"Found sheet '{sheet}' in file '{file}'.")
					if name in raw_data[file][sheet].columns:
						print(f"Found column '{name}' in sheet '{sheet}' of file '{file}'. Updating...")
						df[col] = raw_data[file][sheet][name]
					else:
						print(f"Column '{name}' not found in sheet '{sheet}' of file '{file}'.")
				else:
					print(f"Sheet '{sheet}' not found in file '{file}'.")
			else:
				print(f"File '{file}' not found in raw data.")
	return df

def update_files(raw_folder, update_folder):
	print("Updating files...")

	raw_files = get_excel_files(raw_folder)
	update_files = get_excel_files(update_folder)

	print("Number of output files found:", len(raw_files))
	print("Number of custom files found:", len(update_files))

	raw_data = load_excel_files_into_dict(raw_files)

	for update_file in update_files:
		with pd.ExcelWriter(update_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
			book = writer.book
			for sheet_name in book.sheetnames:
				df = pd.read_excel(update_file, sheet_name=sheet_name)
				updated_df = update_columns(df, raw_data)
				updated_df.to_excel(writer, sheet_name=sheet_name, index=False)

	print("Files updated successfully.")