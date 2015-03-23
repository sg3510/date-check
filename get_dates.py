import json, re
import mechanize
from bs4 import BeautifulSoup
import time, datetime
import random

# read settings file
with open('settings.conf') as data_file:
	conf = json.load(data_file)


br = mechanize.Browser()
br.set_handle_robots(False)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
br.open("https://driverpracticaltest.direct.gov.uk/application?execution=e1s1")

# Wait random period to avoid CAPTCHAs
time.sleep(1 + random.randrange(12,245)/100.0)


br.select_form(nr=0)
br.form.find_control(name="testTypeCar", id='test-type-car')
br.method = "POST"
br.submit()
print br.geturl()

time.sleep(1 + random.randrange(12,245)/100.0)

br.form = list(br.forms())[0]
br['driverLicenceNumber'] = conf['driverLicenceNumber']
br['specialNeeds'] = ['false']
resp = br.submit()
print br.geturl()

time.sleep(1 + random.randrange(12,245)/100.0)

br.form = list(br.forms())[0]
br['testCentreName'] = conf['testCentreName']
br.submit()
print br.geturl()

time.sleep(1 + random.randrange(12,245)/100.0)

link = br.find_link(text_regex=r"Choose")
br.open(br.click_link(link))
print br.geturl()

time.sleep(1 + random.randrange(12,245)/100.0)

br.form = list(br.forms())[0]
br['preferredTestDate'] = conf['preferredTestDate']
response = br.submit()
soup = BeautifulSoup(response.read())

dt_min = datetime.datetime(conf['minYear'], conf['minMonth'], conf['minDay'])
dt_max = datetime.datetime(conf['maxYear'], conf['maxMonth'], conf['maxDay'])

for a in soup('ul')[1].findAll('span'):
	# time.strptime(a.contents[0], "%A %d %B %Y %I:%M%p")
	dt = datetime.datetime(*time.strptime(a.contents[0], "%A %d %B %Y %I:%M%p")[:6])
	if (dt_min < dt) and (dt_max > dt):
		print "found!"
		print a.contents[0]
	# print a.contents[0]