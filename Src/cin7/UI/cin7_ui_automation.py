from Src.access import cin7_username, cin7_password
from Src.helpers.ui_helpers import *
from Src.cin7.UI.cin7_locators import *


def login(driver, username, password):
	clear_and_send_keys(driver, LOGIN_USERNAME, username)
	clear_and_send_keys(driver, LOGIN_PASSWORD, password)
	click_and_wait(driver, LOGIN_PASSWORD_SUBMIT)
	wait_for_user_input()
	wait_for_element(driver, SEARCH_BUTTON)

def cin7_get_ui_report():
	driver = setup_webdriver()
	try:
		open_page(driver, CIN7_AGED_INVENTORY_URL)
		login(driver, cin7_username(), cin7_password())
		return get_report(driver)
	finally:
		close(driver)

def get_report(driver):
	clear_and_send_keys(driver, START_DATE_FIELD, "01-01-2000")
	click_and_wait(driver, SEARCH_BUTTON)
	wait_for_user_input()
	click_and_wait(driver, REPORT_DOWLOAD_CSV)
	return wait_and_rename_downloaded_file(output_folder_path()+"downloads", "cin7_aged_report.csv")