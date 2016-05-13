#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import randint
from .agents import agents

import requests
import re
import os
import socket
import time
import urllib2
import urllib
import json
# Download SocksiPy - A Python SOCKS client module. ( http://code.google.com/p/socksipy-branch/downloads/list )
import socks

ENV = os.environ.get('ENV', 'production')
# On wich port Tor's proxy is avalaible
TOR_PROXY_PORT = int( os.environ.get('TOR_PROXY_PORT', 9050) )
# Maximum throttle delay
THROTTLE_MAX = int( os.environ.get('THROTTLE_MAX', 3) )

def setup():
    # Equal 0 if the TOR_PROXY_PORT is open
    if socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(('127.0.0.1', TOR_PROXY_PORT)) == 0:
        # Tor must listen for SOCKS request on 9050
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", TOR_PROXY_PORT)
        socket.socket = socks.socksocket
        # Notify the user
        print 'Your requests are routed throught Tor'
    # Ensure the timeout is limited to 20 seconds
    socket.setdefaulttimeout(20)

# fetch_page sets up the scraper and the VPN, returns the contents of the page

def fetch_page(url, throttle=(ENV == 'production'), postdata = None):

    if throttle: time.sleep(randint(0, THROTTLE_MAX))

    request = urllib2.Request(url, postdata)
    request.add_header('Cache-Control','max-age=0')
    request.add_header('User-Agent', agents[randint(0,len(agents)-1)], )
    request.add_header('Accept', 'application/json,text/plain,text/html,application/xhtml+xml,application/xml, */*')
    response = urllib2.urlopen(request)

    return response.read()


def regex(needle, haystk, transform=lambda a:a):
    haystk = str(haystk) if type(haystk) is not str else haystk
    match = re.search(r''+needle+'', haystk, re.MULTILINE|re.DOTALL|re.IGNORECASE)
    res = match.group(1) if match != None else None
    return transform(res)

def booleanize(val, null=None):
    if type(val) is bool:
        return val
    elif type(val) is int:
        return bool(val)
    elif val == 'n':
        return False
    elif val == 'y':
        return True
    else:
        return null

def convert(amount, from_currency):

    currencies = {
        "DKK": 0.13,
        "CZK": 0.037,
        "PLN": 0.24,
        "GBP": 1.40,
        "SEK": 0.11,
        "CHF": 0.920587,
        "HUF": 0.0032,
        "BRL": 0.25,
        "VND": 0.000039,
        "EUR": 1
    }

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        print "Invalid amount"
        return False

    return amount * currencies[from_currency]

def clean_amounts(totalRent=0, baseRent=0, serviceCharge=0, livingSpace=None, currency='EUR'):

    baseRent = float(baseRent)
    totalRent = float(totalRent)
    livingSpace = float(livingSpace)

    try:
        serviceCharge = float(serviceCharge)
    except (ValueError, TypeError):
        serviceCharge = 0

    # Computes totalRent and baseRent if they're missing
    if totalRent == 0: totalRent = baseRent + serviceCharge
    if baseRent == 0: baseRent = totalRent - serviceCharge

    # Checks for bogus ads
    if totalRent < 30 or totalRent > 25000 or livingSpace < 3 or livingSpace > 1000:
        return False

    if serviceCharge == 0:
        serviceCharge = None

    return {
        "baseRent": convert(baseRent, currency),
        "baseRentOriginalCurrency": baseRent,
        "serviceCharge": convert(serviceCharge, currency),
        "serviceChargeOriginalCurrency": serviceCharge,
        "totalRent": convert(totalRent, currency),
        "totalRentOriginalCurrency": totalRent,
        "livingSpace": livingSpace,
        "pricePerSqm": convert(totalRent, currency) / livingSpace,
        "currency": currency
    }

def geocode(address, country):

    geocoder  = "http://nominatim.openstreetmap.org/search?"
    geocoder += "format=json&"
    geocoder += "limit=10&"
    geocoder += "bounded=1&"
    geocoder += "osm_type=N&"
    geocoder += "countrycodes=%s&" % country
    geocoder += "q=%s&" % urllib.quote_plus(address)

    page = fetch_page(geocoder)
    data = json.loads(page)

    if len(data) > 0:
        return {
            "lat" : float(data[0]["lat"]),
            "lng" : float(data[0]["lon"])
        }
    else:
        return {
            "lat" : None,
            "lng" : None
        }

def convert_in_meters(string, separator):
    if (separator in string):
        feet = string.split(separator)[0]
        inches = string.split(separator)[1]
        
        inches = inches.replace(" ", "")
        if inches != "" and inches is not None:
            inches = float(inches) * 0.025
        else:
            inches = 0
        return float(feet) * 0.305 + inches

    else:
        feet = string
        return float(feet)

def convert_in_sqm(string):
    return float(string) * 0.092903
    
def find_living_space(desc, no_rooms):
    patterns = [
        {
            # Looks for rooms in feet under the format 5'10" x 3'1"
            "format_finder_expression": "\d{1,2}'[ ]*\d{1,2}\" x \d{1,2}'[ ]*\d{1,2}\"",
            "expression": "(\d{1,2}'[ ]*\d{0,2})(?:\")*(?: max)* x (\d{1,2}'[ ]*\d{0,2})(?:\")*",
            "expect" : "several" # several rooms to add up
        },
        {
            # Looks for rooms in feet under the format 10'2 x 9'3
            "format_finder_expression": "\d{1,2}'\d{1,2} x \d{1,2}'\d{1,2}(?!\")",
            "expression": "(\d{1,2}'\d{0,2})(?: max)* x (\d{1,2}'\d{0,2})",
            "expect" : "several"
        },
        {
            # Looks for "646 sq. Ft."
            "format_finder_expression": "sq\. ft\.",
            "expression": "(\d{3,4})[ ]*sq\. ft\.",
            "expect": "one"
        }
    ]


    # Removes conversions in meters of the format " (3.81m)"
    expression_to_remove = "( \(\d{1,2}.\d{1,2}m\))"
    q = re.compile(expression_to_remove)
    for match in q.finditer(desc):
        desc = desc.replace(match.group(1), "")

    # lower cases
    desc = desc.lower()

    for pattern in patterns:
        format_finder_expression = pattern["format_finder_expression"]
    
        if (re.search(format_finder_expression, desc) is not None):

            expression = pattern["expression"]
            p = re.compile(expression)

            living_space = 0

            if pattern["expect"] == "one":
                match = re.search(expression, desc)
                living_space = convert_in_sqm(match.group(1))

            elif pattern["expect"] == "several":
                for match in p.finditer(desc):
                    living_space += convert_in_meters(match.group(1), "'") *  convert_in_meters(match.group(2), "'")

            if (no_rooms != "NULL" and no_rooms != "None"):
                if living_space/float(no_rooms) < 12 or living_space/float(no_rooms) > 40:
                    return None
                else:
                    return living_space
            
