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
        "pricePerSqm": totalRent / livingSpace,
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
