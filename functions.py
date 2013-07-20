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
    output = subprocess.check_output(["./Adafruit_DHT", "2302", "4"])
    matches = re.search("Temp =\s+([0-9.]+)", output)
    if (not matches):
        time.sleep(3)
        return "error"
    temp = float(matches.group(1))

    # Humidity
    matches = re.search("Hum =\s+([0-9.]+)", output)
    if (not matches):
        time.sleep(3)
        return "ERROR"
    humidity = float(matches.group(1))

    return (temp, humidity)


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


def write_to_gdocs(temp, humidity, ext_temp):
    '''write our data to a google spreadsheet'''
    # Account details for google docs
    email = 'andy.christmas@gmail.com'
    password = 'oknifzuxspiwyobt'
    spreadsheet = 'pitemp'

    # Login with your Google account
    try:
        gc = gspread.login(email, password)
    except:
        print "Unable to log in.  Check your email address/password"
        sys.exit()

    # Open a worksheet from your spreadsheet using the filename
    try:
        worksheet = gc.open(spreadsheet).sheet1
    except:
        print "Unable to open the spreadsheet. \
        Check your filename: %s" % spreadsheet
        sys.exit()

    try:
        values = [datetime.datetime.now(),
                  temp,
                  humidity,
                  ext_temp]
        worksheet.append_row(values)

        #success!
        print "Wrote a row to %s at %s" % (spreadsheet,
                                           datetime.datetime.now())
    except:
        print "Unable to append data.  Check your connection?"

write_to_gdocs(get_external_temp(),
               get_temp()[0],
               get_temp()[1])
