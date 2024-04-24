def f_string(template, *args):
	return template.format(*args)

SHOPIFY_URL = 'https://admin.shopify.com/store/gelous/dashboards'
SHOPIFY_REPORTS_URL_TEMPLATE = 'https://admin.shopify.com/store/gelous/reports/{0}?since={1}&until={2}&over=day'
SHOPIFY_CUSTOMERS_URL_TEMPLATE = 'https://admin.shopify.com/store/gelous/customers?segment_query={0}'

LOGIN_USERNAME = "//input[@id='account_email']"
LOGIN_USERNAME_SUBMIT = "//button[@type='submit']"
LOGIN_PASSWORD = "//*[@id=\"account_password\"]"
LOGIN_PASSWORD_SUBMIT = "//button[@type='submit']"
ANALYTICS = "//span[text()='Analytics']"
REPORT_BY_NAME_TEMPLATE = "//a[contains(@aria-label,'View the {0} report')]"
REPORT_TIME_CONTOLLER_BUTTON = "(//div[contains(@class, 'TimeControlsContainer')]//button[contains(@class, 'Polaris-Button')])[1]"
REPORT_TIME_CONTROLLER_TEMPLATE = "//ul[@class='Polaris-Box Polaris-Box--listReset']/li[contains(@class, 'Polaris-OptionList-Option')]/button[contains(., '{0}')]"
APPLY_BUTTON = "//span[text()='Apply']"
SEARCH_RESULTS = "(//div[contains(@class, 'ResourceList')]//div[contains(@class, 'Row')])[1]"
TABLE = "//table[contains(@class, 'Polaris-DataTable__Table')]"
TABLE_CELL = "(//table[contains(@class, 'Polaris-DataTable__Table')]//tr//th[contains(@class, 'Cell')])[1]"
SEARCH_BAR = "//*[@role=\"search\"]"
HEADER_TEXT = "//h1"
CUSTOMER_COUNT_NUM = "(//span[contains(@class,'CustomerCount')])[1]"
CUSTOMER_COUNT_PERCENT = "(//span[contains(@class,'CustomerCount')])[2]"