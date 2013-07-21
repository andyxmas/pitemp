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
    '''Get the temperature and humidity readings from the DHT22'''
    # Temp
    output = subprocess.check_output(
        ["/home/andy/python/bitbucket/pitemp/Adafruit_DHT", "2302", "4"])
    matches = re.search("Temp =\s+([0-9.]+)", output)
    if (not matches):
        error_internal = "Error getting data from DHT22"
        temp = ""
    else:
        temp = float(matches.group(1))
        error_internal = "OK"

    # Humidity
    matches = re.search("Hum =\s+([0-9.]+)", output)
    if (not matches):
        error_internal = "Error getting data from DHT22"
        humidity = ""
    else:
        humidity = float(matches.group(1))
        error_internal = "OK"

    return (temp, humidity, error_internal)


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
        error_external = "OK"

    except:
        print "had trouble gettin the temp from open weather map..."
        celcius = ""
        error_external = "error getting external temp"

    return celcius, error_external


def write_to_gdocs(temp, humidity, ext_temp, err_int, err_ext):
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
                  ext_temp,
                  err_int,
                  err_ext]
        worksheet.append_row(values)

        #success!
        print "Wrote a row to %s at %s" % (spreadsheet,
                                           datetime.datetime.now())
    except:
        print "Unable to append data.  Check your connection?"

write_to_gdocs(get_external_temp()[0],
               get_temp()[0],
               get_temp()[1],
               get_temp()[2],
               get_external_temp()[1]
               )
