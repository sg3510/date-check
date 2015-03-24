import json, re
import mechanize
from bs4 import BeautifulSoup
import time, datetime
import random

# read settings file
with open('settings.conf') as data_file:
	conf = json.load(data_file)

hour_sec = 60*60

def get_dates_change():
	br = mechanize.Browser()
	br.set_handle_robots(False)
	br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25')]
	br.open("https://driverpracticaltest.direct.gov.uk/login")

	# Wait random period to avoid CAPTCHAs
	time.sleep(1 + random.randrange(92,545)/100.0)

	br.form = list(br.forms())[0]
	br['username'] = conf['driverLicenceNumber']
	br['password'] = conf['applicationRefNumber']
	br.submit()

	# Wait random period to avoid CAPTCHAs
	time.sleep(1 + random.randrange(92,545)/100.0)

	link = br.find_link(url_regex=r'editTestDateTime')
	br.open(br.click_link(link))
	print "** "+br.geturl()

	# Wait random period to avoid CAPTCHAs
	time.sleep(1 + random.randrange(92,545)/100.0)

	br.form = list(br.forms())[0]
	response = br.submit()
	soup = BeautifulSoup(response.read())

	dates = []

	dt_min = datetime.datetime(conf['minYear'], conf['minMonth'], conf['minDay'])
	dt_max = datetime.datetime(conf['maxYear'], conf['maxMonth'], conf['maxDay'])

	for a in soup('ul')[1].findAll('span'):
		# time.strptime(a.contents[0], "%A %d %B %Y %I:%M%p")
		dt = datetime.datetime(*time.strptime(a.contents[0], "%A %d %B %Y %I:%M%p")[:6])
		if (dt_min < dt) and (dt_max > dt):
			print "** - FOUND: "+a.contents[0]
			dates.append(a.contents[0])
		else:
			print '** - avail: '+a.contents[0]
		# print a.contents[0]
	return dates

def get_dates_new():
	br = mechanize.Browser()
	br.set_handle_robots(False)
	br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25')]
	br.open("https://driverpracticaltest.direct.gov.uk/application?execution=e1s1")

	# Wait random period to avoid CAPTCHAs
	time.sleep(1 + random.randrange(92,545)/100.0)


	br.select_form(nr=0)
	br.form.find_control(name="testTypeCar", id='test-type-car')
	br.method = "POST"
	br.submit()
	print "** "+br.geturl()

	time.sleep(1 + random.randrange(92,545)/100.0)

	br.form = list(br.forms())[0]
	br['driverLicenceNumber'] = conf['driverLicenceNumber']
	br['specialNeeds'] = ['false']
	resp = br.submit()
	print "** "+br.geturl()

	time.sleep(1 + random.randrange(92,545)/100.0)

	br.form = list(br.forms())[0]
	br['testCentreName'] = conf['testCentreName']
	br.submit()
	print "** "+br.geturl()

	time.sleep(1 + random.randrange(92,545)/100.0)

	link = br.find_link(text_regex=r"Choose")
	br.open(br.click_link(link))
	print "** "+br.geturl()

	time.sleep(1 + random.randrange(92,545)/100.0)

	br.form = list(br.forms())[0]
	br['preferredTestDate'] = conf['preferredTestDate']
	response = br.submit()
	soup = BeautifulSoup(response.read())

	dates = []

	dt_min = datetime.datetime(conf['minYear'], conf['minMonth'], conf['minDay'])
	dt_max = datetime.datetime(conf['maxYear'], conf['maxMonth'], conf['maxDay'])

	for a in soup('ul')[1].findAll('span'):
		# time.strptime(a.contents[0], "%A %d %B %Y %I:%M%p")
		dt = datetime.datetime(*time.strptime(a.contents[0], "%A %d %B %Y %I:%M%p")[:6])
		if (dt_min < dt) and (dt_max > dt):
			print "** - FOUND: "+a.contents[0]
			dates.append(a.contents[0])
		else:
			print '** - avail: '+a.contents[0]
		# print a.contents[0]
	return dates

def send_mail(dates):
	import smtplib
	from email.MIMEMultipart import MIMEMultipart
	from email.MIMEText import MIMEText
	msg = MIMEMultipart()
	msg['From'] = conf['emailFrom']
	msg['To'] = conf['emailTo']
	msg['Subject'] = conf['emailSubject']
	message = 'Hey '+ conf['emailName'] + ',\n\nThe available dates found are:\n'
	for date in dates:
		message = message + date + '\n'
	message = message + 'Be sure to book ASAP. \nhttps://www.gov.uk/book-driving-test \n\nKind Regards, \nDVLA Checker Bot'
	msg.attach(MIMEText(message))

	mailserver = smtplib.SMTP(conf['smtpServer'],587)
	# identify ourselves to smtp gmail client
	mailserver.ehlo()
	# secure our email with tls encryption
	mailserver.starttls()
	# re-identify ourselves as an encrypted connection
	mailserver.ehlo()
	mailserver.login(str(conf['smtpFromUsername']), str(conf['smtpFromPassword']))

	mailserver.sendmail(conf['emailFrom'],conf['emailTo'],msg.as_string())

	print "** Mail sent!"

	mailserver.quit()



if __name__ == '__main__':
	print "Welcome "+conf['emailName']+", I'll be checking the DVLA for dates that suit you."
	print "I'll be senging emails from "+conf['emailFrom']+" to "+conf['emailTo']+'.'

	dt_min = datetime.datetime(conf['minYear'], conf['minMonth'], conf['minDay'])
	dt_max = datetime.datetime(conf['maxYear'], conf['maxMonth'], conf['maxDay'])
	print "I'm looking for dates between "+dt_min.strftime('%A %d %B')+ " and "+dt_max.strftime('%A %d %B')

	while True:
		now = datetime.datetime.now()
		now_time = now.time()
		if datetime.time(7,30) <= now.time() <= datetime.time(22,30):        
			print "* Checking DVLA"
			try:
				dates = get_dates_new()
				if dates:
					send_mail(dates)
				else:
					print "** No dates found, maybe some will turn up next time?"
			except Exception, e:
				print str(e) + '\n/!\Failed, maybe CAPTCHA turned up?'
		else:
			print "* Not checking due to time"
		wait_time = hour_sec + hour_sec*random.gauss(1.3,0.5)
		print '* Waiting %.2f hours before retrying at %s' % ((wait_time/3600.00), (datetime.datetime.now()+datetime.timedelta(0,wait_time)).time().strftime("%I:%M:%S %p"))
		time.sleep(wait_time)


		# dates = get_dates_new()
		# dates = ['Friday 27 March 2015 10:14am']
		# send_mail(dates)