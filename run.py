#!/usr/bin/python

import subprocess
import re
import sys
import time
import datetime
import gspread
import requests
import xml.etree.ElementTree as ET


# ===========================================================================
# Google Account Details
# ===========================================================================

# Account details for google docs
email       = 'andy.christmas@gmail.com'
password    = 'oknifzuxspiwyobt'
spreadsheet = 'DHT 2'

# ===========================================================================
# Example Code
# ===========================================================================


# Login with your Google account
try:
  gc = gspread.login(email, password)
except:
  print "Unable to log in.  Check your email address/password"
  sys.exit()

# Open a worksheet from your spreadsheet using the filename
try:
  worksheet = gc.open(spreadsheet).sheet1
  # Alternatively, open a spreadsheet using the spreadsheet's key
  # worksheet = gc.open_by_key('0AlqDnT_7ezt7dDYzbk5OQ0IzMklhYXU5dExZX0VYZGc')
except:
  print "Unable to open the spreadsheet.  Check your filename: %s" % spreadsheet
  sys.exit()

# Continuously append data
while(True):
  # Run the DHT program to get the humidity and temperature readings!

  output = subprocess.check_output(["./Adafruit_DHT", "2302", "4"]);
  print output
  matches = re.search("Temp =\s+([0-9.]+)", output)
  if (not matches):
	time.sleep(3)
	continue
  temp = float(matches.group(1))
  
  # search for humidity printout
  matches = re.search("Hum =\s+([0-9.]+)", output)
  if (not matches):
	time.sleep(3)
	continue
  humidity = float(matches.group(1))

  print "Temperature: %.1f C" % temp
  print "Humidity:    %.1f %%" % humidity
 
  # Get the current temperature
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
  
  ext_temp = get_external_temp()
  print "External Temp: %.1f C" % ext_temp
 
  # Append the data in the spreadsheet, including a timestamp
  try:
    values = [datetime.datetime.now(), temp, humidity, ext_temp]
    worksheet.append_row(values)

    # Wait 30 minutes before continuing
    print "Wrote a row to %s at %s" % (spreadsheet, datetime.datetime.now())
    time.sleep(1800)

  except:
    print "Unable to append data.  Check your connection?"
    sleep(100)
