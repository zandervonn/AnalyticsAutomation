from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from pandas import *
from pyautogui import *
import csv
import time

webdriver_path = 'C:\\Users\\Zander\\.wdm\\chromedriver\\72.0.3626.7\\win32\\chromedriver.exe'
target_url = 'https://google.com'

def setup_webdriver():
	options = Options()
	# options.add_argument('--headless')  # Run in headless mode
	driver = webdriver.Chrome(options=options)
	return driver

def navigate_to(driver, url):
	driver.get(url)
	time.sleep(2)

def extract_data(driver):
	data = []
	return data

def write_data_to_csv(data, file_path):
	with open(file_path, mode='w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(data.keys())
		writer.writerow(data.values())

def extract_vi(driver):
	navigate_to(driver, target_url)
	data = extract_data(driver)
	# write_data_to_csv(data, output_csv_file)

def UIMain():
	driver = setup_webdriver()
	try:
		extract_vi(driver)
	finally:
		driver.quit()