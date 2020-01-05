import csv
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Настройки хрома
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-setuid-sandbox")
chrome_options.add_argument("--headless")
 

def inputform():
	# Форма для ввода данных о покойнике
	name = input('Enter full name, separated with spaces:')
	temp = name.split(" ")
	nameList = {'firstname': temp[0], 'middlename': temp[1],'lastname':temp[2]}
	born = input('(Opional)Add year born: ')
	died = input('(Opional)Add year died: ')
	cemetery = input('(Opional)Add cemetery location: ')
	global driver
	driver = webdriver.Chrome("/home/crowcrxst/Python/Chromium/chromedriver", options=chrome_options)
	driver.get('https://www.findagrave.com/')
	print('Searching for {}'.format(nameList['firstname'] + " " + nameList['middlename'] + " " 
									+ nameList['lastname']))
	searchform(nameList, born, died, cemetery)


def searchform(nameList, born, died, cemetery):
	# Форма для ввода данных на сайте
	firstname = driver.find_element_by_xpath('//input[@id="firstname"]')
	firstname.send_keys(nameList['firstname'])
	middlename = driver.find_element_by_xpath('//input[@id="middlename"]')
	middlename.send_keys(nameList['middlename'])
	lastname = driver.find_element_by_xpath('//input[@id="lastname"]')
	lastname.send_keys(nameList['lastname'])
	# Дополнительная форма
	if born is not None:
		birthdate = driver.find_element_by_xpath('//input[@id="birthyear"]')
		birthdate.send_keys(born)
	if died is not None:
		deathdate = driver.find_element_by_xpath('//input[@id="deathyear"]')
		deathdate.send_keys(died)
	if cemetery is not None:
		cemeteryloc = driver.find_element_by_xpath('//input[@id="location"]')

	# Кнопка запроса
	search = driver.find_element_by_xpath('//button[@type="submit"]')
	sleep(1)
	search.click()

	# создание файла для записи данных
	with open('GEDCOM.csv', 'a+', encoding='utf-8') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(["Name", "Birth", "Death", "Burial"])

	# создание списков покойников
	global family_list, relatives_list, seen
	family_list = []
	relatives_list = []
	seen = []

	# Добавление покойника в список увиденных
	candidate_url = driver.find_element_by_xpath('//a[@class="memorial-item"]')
	seen.append(candidate_url.get_attribute('href'))
	# Переход на страницу покойника
	candidate = driver.find_element_by_xpath('//a[@class="memorial-item"]').click()
	infoscrape()
	familyscrape()
	famscrape()
	

def infoscrape():
	# Форма для сбора информации 
	name = driver.find_element_by_xpath('//h1[@itemprop="name"]')
	birth = driver.find_element_by_xpath('//time[@itemprop="birthDate"]')
	death = driver.find_element_by_xpath('//span[@itemprop="deathDate"]')
	burialcity = driver.find_element_by_xpath('//span[@id="cemeteryCityName"]') 
	burialcounty = driver.find_element_by_xpath('//span[@id="cemeteryCountyName"]') 
	burialstate = driver.find_element_by_xpath('//span[@id="cemeteryStateName"]') 
	burialcountry = driver.find_element_by_xpath('//span[@id="cemeteryCountryName"]')
	print('Name: ' + name.text + ", Born: " + birth.text + ", Died: " + death.text)
	print('Burial: ' + burialcity.text + ", " + burialcounty.text + ", " + 
							burialstate.text + ", " + burialcountry.text)

	# создание файла для записи данных
	with open('GEDCOM.csv', 'a+', encoding='utf-8', newline='') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow([name.text, birth.text, death.text, burialcity.text + ", " 
			+ burialcounty.text + ", " + burialstate.text + ", " + burialcountry.text])


def familyscrape():
# Поиск семьи покоиника
	family = driver.find_elements_by_xpath('//div[@class="col-sm-6"]')
	for pers in family:
		with open('GEDCOM.csv', 'a+', encoding='utf-8', newline='') as f:
			writer = csv.writer(f, delimiter=',')
			writer.writerow([pers.text])
			print(pers.text)

def famscrape():
	# Форма для сбора информации по семье
	with open('GEDCOM.csv', 'a+', encoding='utf-8') as f:
		writer = csv.writer(f, delimiter=',')
	family = driver.find_elements_by_xpath('//div[@class="media-body"]/a[@href]')
	for member in family:
		family_list.append(member.get_attribute('href'))
	for fam in family_list:
		if fam not in seen:
			driver.execute_script("window.open('');") 
			driver.switch_to_window(driver.window_handles[1])
			driver.get(fam)
			sleep(1)
			infoscrape()
			familyscrape()
			seen.append(fam)
			relatives = driver.find_elements_by_xpath('//div[@class="media-body"]/a[@href]')
			for relative in relatives:
				relatives_list.append(relative.get_attribute('href'))
			driver.execute_script("window.close('');")
			driver.switch_to_window(driver.window_handles[0])
	print('Total {} familly members scraped'.format(len(family_list)))
	print('Found {} relatives, do you wish to collect their information as well?'.format(len(relatives_list)))
	while True:
		prompt = input('Yes/No?: ').lower()
		if prompt == 'yes' or 'y':
			relativesscrape()
		elif prompt == 'no' or 'n':
			break
		else:
			print('Hm?')


def relativesscrape():
	# Форма для сбора по дальним родственникам
	with open('GEDCOM.csv', 'a+', encoding='utf-8') as f:
		writer = csv.writer(f, delimiter=',')
	for relative in relatives_list:
		if relative not in seen:
			driver.execute_script("window.open('');") 
			driver.switch_to_window(driver.window_handles[1])
			driver.get(relative)
			sleep(1)
			infoscrape()
			familyscrape()
			seen.append(relative)
			more_relatives = driver.find_elements_by_xpath('//div[@class="media-body"]/a[@href]')
			for another_relative in more_relatives:
				relatives_list.append(another_relative.get_attribute('href'))
			driver.execute_script("window.close('');")
			driver.switch_to_window(driver.window_handles[0])	
	print('Found more {} relatives'.format(len(more_relatives)))
	print('Another round?: ')
	while True:
		prompt = input('Yes/No?: ').lower()
		if prompt == 'yes' or 'y':
			relativesscrape()
		elif prompt == 'no' or 'n':
			break
		else:
			print('Hm?')

	
inputform()