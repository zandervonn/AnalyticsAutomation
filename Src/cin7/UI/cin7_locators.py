def f_string(template, *args):
	return template.format(*args)

CIN7_AGED_INVENTORY_URL_NZ = 'https://insights.cin7.com/Reports/Default?idCustomerAppsLink=936717&strKey=1#/'
CIN7_AGED_INVENTORY_URL_AUS = 'https://insights.cin7.com/Reports/Default?idCustomerAppsLink=1137753&strKey=1#/'
CIN7_STOCK_REPORT_URL_NZ = "https://insights.cin7.com/Reports/PivotGrid?idCustomerAppsLink=936717&strKey=17#/"
CIN7_STOCK_REPORT_URL_AUS = "https://insights.cin7.com/Reports/PivotGrid?idCustomerAppsLink=1137777&strKey=7#/"
CIN7_DASHBOARD_URL_NZ = "https://go.cin7.com/Cloud/Dashboard/HomePageDashboard.aspx"
CIN7_DASHBOARD_URL_AUS = "https://go.cin7.com/Cloud/Dashboard/HomePageDashboard.aspx"

LOGIN_USERNAME = "//input[contains(@id,'username')]"
LOGIN_PASSWORD = "//input[contains(@id,'password')]"
LOGIN_PASSWORD_SUBMIT = "//input[contains(@type,'submit')]"
LOGO = "//img[contains(@class,'logo-short')]"

SEARCH_BUTTON = "//input[contains(@type,'submit')]"
START_DATE_FIELD = "//input[contains(@id,'StartDate')]"
END_DATE_FIELD = "//input[contains(@id,'EndDate')]"
AGE_REPORT_DATE_2000 = "//span[contains(@class,'gridTitle') and contains(text(),'2000')]"
REPORT_DOWLOAD_CSV = "(//div[contains(@class,\'button-content\')])[1]"

DOWNLOAD_STOCK_REPORT_BUTTON = "(//div[contains(@id,'SaveAsButton')])[1]"

DASHBOARD_DATA_BOX = "//div[contains(@class,'data-box-header extend')]"
DASHBOARD_DATA_BOX_TITLE = './/div[contains(@class, "data-box-title")]'
DASHBOARD_DATA_BOX_VALUE = './/div[contains(@class, "data-box-value")]'

