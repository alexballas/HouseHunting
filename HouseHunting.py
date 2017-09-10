#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import time
import logging
from bs4 import BeautifulSoup
from urlparse import urlparse
import os.path
import shutil
import filecmp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint
from time import sleep

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',filename='hh.log',level=logging.DEBUG)

def getUrlDetails( url ):
	parsed_uri = urlparse(url)
	domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

	try:
		connection = urllib2.urlopen(url)
		html_doc = connection.read()
		connection.close()
	except urllib2.HTTPError, e:
		return e.getcode()

	return (domain,html_doc)

def sendMailOnDiff ( difftext ):
	gmail_user = "" #CHANGE THIS
	gmail_pwd = "" #CHANGE THIS

	src = gmail_user
	dst = "" #CHANGE THIS

	msg = MIMEMultipart()
	msg['Subject'] = 'Νέες Αγγελίες ' + time.strftime("%d/%m/%Y")
	msg['From'] = src
	msg['To'] = dst
	msg.attach(MIMEText(difftext))
	s = smtplib.SMTP("smtp.gmail.com", 587)
	s.ehlo()
	s.starttls()
	s.ehlo()
	s.login(gmail_user, gmail_pwd)
	s.sendmail(src, dst, msg.as_string())
	s.close()

def compare(File1,File2):
    f1 = open(File1, 'r').readlines()
    f2 = open(File2, 'r').readlines()
    indexa = 0
    indexb = 0
    diffText = ""
    while(1):
      try:
          if f1[indexa][:-1] ==  f2[indexb][:-1]:
              indexa +=1
              indexb +=1
          elif f1[indexa][:-1] != f2[indexb][:-1]:
              diffText += f1[indexa][:-1].strip() + "\n"
              indexa += 1
      except IndexError:
          break
    return diffText

def main():

	url = '' #CHANGE THIS
	file1 = "/tmp/.spitipy.tmp1"
	file2 = "/tmp/.spitipy.tmp2"

	urlDetails = getUrlDetails(url)
	soup = BeautifulSoup(urlDetails[1], 'html.parser')
	result = soup.find_all("div", {"class":"lazy"})

	f1 = open(file1, "w")

	for element in result:
		for last_string_elements in element.find("p").stripped_strings:
			pass
		f1.write(urlDetails[0][:-1] + element.find("a", {"class":"r_t"}).get('href').encode("utf-8") + "\n")
		f1.write(last_string_elements.encode("utf-8") +"\n")
		if (element.find("li", {"class":"r_price"})):
			f1.write(element.find("li", {"class":"r_price"}).text.encode("utf-8")+"\n")
		else:
			f1.write("- €\n")
		f1.write("\n")

	f1.close()

	if not os.path.isfile(file2):
		if os.path.isfile(file1):
			print "First run ..."
			shutil.copy(file1, file2)
	else:
		if os.path.isfile(file1):
			if filecmp.cmp(file1, file2):
				print "No updates, exiting ..."
			else:
				f1 = open(file1, "r")
				f2 = open(file2, "r")
				for line_f1 in f1:
					logging.info('File 1 contents: %s', line_f1)
				for line_f2 in f2:
					logging.info('File 2 contents: %s', line_f2)
				f1.close()
				f2.close()
				sendMailOnDiff(compare(file1,file2))
				shutil.copy(file1, file2)
				print "Not the same File"

if __name__ == "__main__":
    while 1:
    	main()
    	sleep(randint(300,600))
