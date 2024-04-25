def f_string(template, *args):
	return template.format(*args)

STARSHIPIT_URL = 'https://app.starshipit.com/templates/admin4/reports.aspx'

LOGIN_USERNAME = "//input[contains(@id,'UserName')]"
LOGIN_PASSWORD = "//input[contains(@id,'Password')]"
LOGIN_PASSWORD_SUBMIT = "//a[contains(@id,'LoginButton')]"

GENERATE_BUTTON = "//input[contains(@value,'Generate') and not (contains(@type,'hidden'))]"
START_DATE_FIELD = "//input[contains(@id,'StartDate') and (contains(@class,'TextBox'))]"
END_DATE_FIELD = "//input[contains(@id,'EndDate') and (contains(@class,'TextBox'))]"
CHILD_ORDER_CHECKBOX = "//tr//span[contains(text(),'Include child accounts')]/..//span[contains(@class,'ToggleCheckbox')]"
REPORT_STATUS_READY = "//table[contains(@class,'Master')]//tbody/tr[1]/td[contains(text(),'Ready')]"
REPORT_DOWLOAD_CSV = "//table[contains(@class,'Master')]//tbody/tr[1]/td//a[(contains(@id,'CSV') and not (contains(@id,'Xlsx')))]"