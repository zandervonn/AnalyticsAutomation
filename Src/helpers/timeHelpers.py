from datetime import datetime, timedelta

def get_dates(from_date, last, num):
	# Determine the base date
	if from_date == 'today':
		base_date = datetime.now()
	else:
		base_date = datetime.strptime(from_date, '%Y-%m-%d')

	delta = timedelta(days=num)
	# Calculate 'since' based on the 'last' period and 'num'
	if last == 'weeks':
		delta = timedelta(weeks=num)
	elif last == 'days':
		delta = timedelta(days=num)
	elif last == 'months':  # Approximate month as 30 days
		delta = timedelta(days=30*num)

	since = (base_date - delta).strftime('%Y-%m-%d')
	until = base_date.strftime('%Y-%m-%d')

	return since, until