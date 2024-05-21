
import pytz
from Src.helpers.file_helpers import find_path_upwards
from datetime import datetime, timedelta, timezone

LAST_RUN_FILE_PATH = find_path_upwards(r"config\config.txt")

# todo clean up
def get_dates(from_date, time_span, num):
	# Set the timezone to New Zealand
	tz = pytz.timezone('Pacific/Auckland')

	# Determine the base date
	if from_date == 'today':
		base_date = datetime.now(tz)
	elif from_date == 'sunday':
		now = datetime.now(tz)
		if now.weekday() == 6:  # If today is Sunday
			base_date = now
		else:
			# Adjust base_date to the most recent past Sunday
			days_behind = (now.weekday() + 1) % 7
			base_date = now - timedelta(days=days_behind)
		base_date = base_date.replace(hour=23, minute=59, second=59, microsecond=0)  # Set to 23:59:59 on Sunday
	else:
		base_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M:%S')
		base_date = tz.localize(base_date)

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
	until = base_date.strftime('%Y-%m-%dT%H:%M:%S')
	since = base_date - delta
	# Set the 'since' to 00:00 on the Monday just before the past Sunday
	since = since.replace(hour=0, minute=0, second=0, microsecond=0)
	since = (since + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')  # Adjust for the Monday start

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