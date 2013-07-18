#!/usr/bin/python

import subprocess
import re
import sys
import time
import datetime
import gspread
import requests
import xml.etree.ElementTree as ET


def get_temp():
	'''Get the temperature and humidity readings from the DHT22'''
	# Temp
	output = subprocess.check_output(["./Adafruit_DHT", "2302", "4"]);
	matches = re.search("Temp =\s+([0-9.]+)", output)
  	if (not matches):
		time.sleep(3)
		continue
  	temp = float(matches.group(1))

  	# Humidity
  	matches = re.search("Hum =\s+([0-9.]+)", output)
  	if (not matches):
		time.sleep(3)
		continue
  	humidity = float(matches.group(1))

  	return {'temp': temp, 'humidity': humidity}


def get_external_temp():
	'''using openweathermap, get the tempertare at time of call'''
    baseurl = "http://api.openweathermap.org/data/2.5/weather"
    query = "?q=salhouse&mode=xml"
    url = baseurl + query
    try:
    	r = requests.get(url)
      	root = ET.fromstring(r.text)
      	kelvin = float(root[1].attrib.get('value'))
      	celcius = kelvin - 272.15
      	return celcius      

    except:
      	print "had trouble gettin the temp from open weather map..."
      	return "error getting data"


print "external temp: %s, internal temp: %s, humidity: %s." % (
  	get_external_temp(), get_temp['temp'], get_temp['humidity'])
