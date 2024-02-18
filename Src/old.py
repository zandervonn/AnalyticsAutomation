import time
import math
import re



def searchText(var):
	#driver.find_element_by_name('q').clear() #clears text
	browser.find_element_by_name('q').send_keys(var) #inserts text to feild

	time.sleep(0.5) #wait for popup
	browser.find_element_by_name('btnK').click() #click search button

def setDropdown(div,index):
	s1= Select(browser.find_element_by_id(div))
	s1.select_by_index(index)


def setup():

	url = 'http://google.com'

	browser.get(url)

def secondTab(site2):
	browser.execute_script("window.open('about:blank', 'tab2');") #initiate second tab
	browser.switch_to.window("tab2")        #switches to second tab
	browser.get(site2)          #opens on new tab

def switchTab(num):
	browser.switch_to_window(browser.window_handles[num]) #switch tabs 0 = first, 1 = second ...

def getText(div):
	content = browser.find_elements_by_xpath(div)[0].text # gets text from div
	print(content)
	return content

def getWeight(div):
	#    string = getText(div)
	numbers = re.findall('\d+',div)
	num = int(numbers[0])
	if num > 100:
		val = num + 70
		val = val / 100
		val = int(math.ceil(val/5)*5)
		val = val / 10
	else:
		val = num * 10
		val = int(math.ceil(val/5)*5)
		val = val / 10
	print(val)
	return val

setup()

secondTab('http://bing.com')

switchTab(0)

search = getText('//div[@id="SIvCob"]')

input("Press Enter to continue...")

searchText(search)
