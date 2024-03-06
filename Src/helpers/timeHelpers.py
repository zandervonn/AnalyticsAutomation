from datetime import datetime, timedelta, timezone

def get_dates(from_date, last, num):
	# Determine the base date
	if from_date == 'today':
		base_date = datetime.now()
	else:
		base_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M:%S')

	delta = timedelta(days=num)
	# Calculate 'since' based on the 'last' period and 'num'
	if last == 'weeks':
		delta = timedelta(weeks=num)
	elif last == 'days':
		delta = timedelta(days=num)
	elif last == 'months':  # Approximate month as 30 days
		delta = timedelta(days=30*num)

	since = (base_date - delta).strftime('%Y-%m-%dT%H:%M:%S')
	until = base_date.strftime('%Y-%m-%dT%H:%M:%S')

	return since, until

LAST_RUN_FILE_PATH = r"C:\Users\Zander\IdeaProjects\Automation-Gel\Src\config"

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