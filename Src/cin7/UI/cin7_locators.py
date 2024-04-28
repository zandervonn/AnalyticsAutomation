def f_string(template, *args):
	return template.format(*args)

CIN7_AGED_INVENTORY_URL = 'https://insights.cin7.com/Reports/Default?idCustomerAppsLink=936717&strKey=1#/'

LOGIN_USERNAME = "//input[contains(@id,'username')]"
LOGIN_PASSWORD = "//input[contains(@id,'password')]"
LOGIN_PASSWORD_SUBMIT = "//input[contains(@type,'submit')]"

SEARCH_BUTTON = "//input[contains(@type,'submit')]"
START_DATE_FIELD = "//input[contains(@id,'StartDate')]"
END_DATE_FIELD = "//input[contains(@id,'EndDate')]"
REPORT_DOWLOAD_CSV = "(//div[contains(@class,\'button-content\')])[1]"