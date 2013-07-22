#! /usr/bin/env python

import subprocess
import re
import sys
import time
import datetime
import gspread
import requests
import xml.etree.ElementTree as ET


def get_temp():
    """Get the temperature and humidity readings from the DHT22"""
    count = 0
    while True:
        # Temp
        output = subprocess.check_output(
            ["/home/andy/python/bitbucket/pitemp/Adafruit_DHT", "2302", "4"])
        count += 1
        print ("Attempt %s: %s") % (count, output)
        temp_match = re.search("Temp =\s+([0-9.]+)", output)
        humid_match = re.search("Hum =\s+([0-9.]+)", output)

        # if the beginning of output contains temp and numbers,
        # we can assume we are getting valid data
        if temp_match:
            temp = float(temp_match.group(1))
            humidity = float(humid_match.group(1))
            break

    return (temp, humidity)


def get_external_temp():
    """using openweathermap, get the tempertare at time of call"""
    baseurl = "http://api.openweathermap.org/data/2.5/weather"
    query = "?q=salhouse&mode=xml"
    url = baseurl + query
    r = requests.get(url)
    root = ET.fromstring(r.text)
    kelvin = float(root[1].attrib.get('value'))
    celcius = kelvin - 272.15
    return celcius


def write_to_gdocs(temp, ext_temp, humidity):
    """write our data to a google spreadsheet"""
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
                  ext_temp,
                  humidity]
        worksheet.append_row(values)

        #success!
        print "Wrote a row to %s at %s" % (spreadsheet,
                                           datetime.datetime.now())
    except:
        print "Unable to append data.  Check your connection?"

write_to_gdocs(get_temp()[0],
               get_external_temp(),
               get_temp()[1]
               )
