from datetime import datetime, timedelta, timezone

from Src.helpers.file_helpers import find_path_upwards

LAST_RUN_FILE_PATH = find_path_upwards(r"config\config.txt")

from datetime import datetime, timedelta

def get_dates(from_date, time_span, num):
	# Determine the base date
	if from_date == 'today':
		base_date = datetime.now()
	elif from_date == 'sunday':
		now = datetime.now()
		if now.weekday() == 6:  # If today is Sunday (weekday() returns 6 for Sunday)
			base_date = now  # Use the current time
		else:
			# Adjust base_date to the most recent past Sunday
			days_behind = (now.weekday() + 1) % 7  # Calculate days since last Sunday
			base_date = now - timedelta(days=days_behind)
			base_date = base_date.replace(hour=23, minute=59, second=0, microsecond=0)  # Set to 11:59 PM
	else:
		base_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M:%S')

	# Define the time delta based on time_span
	if time_span == 'weeks':
		delta = timedelta(weeks=num)
	elif time_span == 'days':
		delta = timedelta(days=num)
	elif time_span == 'months':  # Approximate month as 30 days
		delta = timedelta(days=30 * num)
	else:
		print("Time span cannot be decoded, calculating by days")
		delta = timedelta(days=num)

	# Calculate the 'since' date
	since = (base_date - delta).strftime('%Y-%m-%dT%H:%M:%S')
	until = base_date.strftime('%Y-%m-%dT%H:%M:%S')

	return since, until

def convert_dates_to_offsets(since, until):
	since_date = datetime.strptime(since, '%Y-%m-%dT%H:%M:%S').date()
	until_date = datetime.strptime(until, '%Y-%m-%dT%H:%M:%S').date()
	current_date = datetime.now().date()

	since_offset = -(current_date - since_date).days
	until_offset = -(current_date - until_date).days

	return f"{since_offset}d", f"{until_offset}d"

def get_last_run_timestamp():
	try:
		with open(LAST_RUN_FILE_PATH, 'r') as file:
			return datetime.strptime(file.read().strip(), '%Y-%m-%dT%H:%M:%S%z')
	except FileNotFoundError:
		return datetime.min.replace(tzinfo=timezone.utc)

def set_last_run_timestamp():
	current_timestamp = datetime.now(timezone.utc)
	with open(LAST_RUN_FILE_PATH, 'w') as file:
		file.write(current_timestamp.strftime('%Y-%m-%dT%H:%M:%S%z'))
	return current_timestamp