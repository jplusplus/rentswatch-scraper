#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of rentswatch-scraper.
# https://github.com/jplusplus/rentswatch-scraper

# Licensed under the LGPL license:
# http://www.opensource.org/licenses/LGPL-license
# Copyright (c) 2015, pirhoo <hello@pirhoo.com>

from .browser import fetch_page, clean_amounts, geocode, regex as fast_regex
from .db import Ad, Report

from .fields import Field

from bs4 import BeautifulSoup
from sqlobject import AND, OR

import reporting
import db
import socket
import pprint
import browser
import urllib2
import formencode

class Scraper(object):

    class Meta:
        # Configuration attributes:
        # must be set within the child class
        country  = ''
        site     = ''
        baseUrl  = ''
        listUrl  = ''
        # CSS selector to retreive an ad's block
        adBlockSelector = '.detail-page-link'

    def __init__(self, max_page=20, debug=False):
        # Setup database table
        db.setup()
        # Setup browser simulator (that can navigate through Tor)
        browser.setup()
        # Instance attributes
        self._max_page = max_page
        self._page = 1
        self._debug = debug
        # Create a pretty printer
        self._pp = pprint.PrettyPrinter(indent=4)
        # Copy the Meta class to a private attributes
        self._meta = self.Meta
        # Copy attributes from Scraper.Meta to the current meta class
        for attr in Scraper.Meta.__dict__.keys():
            # Does NOT import private attributes
            if attr[:1] != '_' and not hasattr(self.Meta, attr):
                # Copy from the parent
                setattr(self._meta, attr, getattr(Scraper.Meta, attr))
        # True if the given name is a field
        is_field = lambda m: isinstance(getattr(self, m), Field)
        # Save fields list
        self._fields = [ m for m in dir(self) if is_field(m) ]
        # Sort the fields
        self._fields.sort(key=lambda f: getattr(self, f)._count)

    @property
    def dup_count(self):
        return reporting.dupCount

    @property
    def series_url(self):
        return self._meta.listUrl + "&p=" + str(self._page)

    def run(self):
        try:
            # Iterates after several pages
            while self._page < self._max_page and self.dup_count < 20:
                try:
                    # Fetch a series of elements
                    self.fetch_series()
                except urllib2.HTTPError as e:
                    print 'Unable to fecth %s' % self.series_url
                # Next page
                self._page = self._page + 1
        # Say bye to the user!
        except KeyboardInterrupt: print '\nThanks, have a nice day!'

    def ok(self, string):
        print u'\033[92m%s\033[0m' % string

    def fail(self, string):
        print u'\033[91m%s\033[0m' % string

    def find_ad_blocks(self, soup):
        # By default we consider the ad block is a link
        return soup.select(self._meta.adBlockSelector)

    def get_fields(self):
        return ( (m, getattr(self, m) ) for m in self._fields )

    def get_ad_href(self, soup):
        # By default we consider the ad block is a link
        href = soup.get('href')
        # Should be add the baseUrl to the link?
        return href if href.startswith(self._meta.baseUrl) else self._meta.baseUrl + href

    def get_ad_id(self, soup):
        href = self.get_ad_href(soup)
        # By default we use the ad href to extract an ending id
        return fast_regex("/(\d+)(\.html?)?$", href)

    # True if the ad has already been scraped
    def is_scraped(self, siteId):
        return Ad.select(
            AND(Ad.q.siteId == str(siteId), Ad.q.site == self._meta.site)
        ).count() > 0

    # True if the ad has already been reported
    def has_issue(self, siteId):
        return Report.select(
            AND(Report.q.siteId == str(siteId), Report.q.site == self._meta.site)
        ).count() > 0

    # Prepare the value to be saved
    def prepare(self, name, value):
        return value

    def transform_page(self, page):
        return page

    def get_series(self):
        content = self.transform_page( fetch_page( self.series_url ) )
        return BeautifulSoup(content, 'html.parser')

    def fetch_series(self):
        series = self.get_series()
        # Extract ad' blocks from the series' soup
        for ad_block in self.find_ad_blocks(series):
            # Gets href and siteId from the link
            href   = self.get_ad_href(ad_block)
            siteId = self.get_ad_id(ad_block)
            try:
                # No URL found, no ad to fetch
                if href is None: continue
                # Checks that we didn't scan this ad yet
                if self.is_scraped(siteId) or self.has_issue(siteId):
                    # Raise a duplicate error (which is not saved)
                    raise reporting.DuplicateError(self._meta.country, self._meta.site, siteId)
                # Fetch the ad
                ad, values = self.fetch_ad(href, siteId)
                # Inform the user
                self.ok(u"[SUCCESS] Ad %s scraped." % siteId)
                # Print out the extracted values in debug mode
                if self._debug: self._pp.pprint(values)
            # Cache common errors
            except reporting.REPORTABLE_ERRORS as e:
                # Simply save the report
                e.save()
                # Inform the user
                self.fail(u"[ERROR] Ad %s was wrong: %s." % (siteId, e.name))
                # And continue to the next ad
                continue

    def fetch_ad(self, href, siteId):
        try:
            content = fetch_page(href)
        except socket.timeout as e:
            raise reporting.TimeoutError(self._meta.country, self._meta.site, siteId)
        except urllib2.URLError as e:
            raise reporting.UnreachableError(self._meta.country, self._meta.site, siteId)
        # Ad page soup
        soup = BeautifulSoup(content, 'html.parser')
        # Some fields are present in every ad
        defaultFields = dict(
            siteId=siteId,
            country=self._meta.country,
            site=self._meta.site,
            sourceUrl=href
        )
        try:
            # A dictionnary of every saved value
            values = self.extract_ad(soup, siteId)
            # Merge both dictionnary
            values.update(defaultFields)
            # Remove virtual values (key starting by _)
            values = {k: v for k, v in values.iteritems() if not k[:1] == '_' }
            # Builds and returns the ad
            return Ad(**values), values
        except (formencode.Invalid, ValueError,) as e:
            # Print out the invalid error
            if self._debug: self._pp.pprint(e)
            raise reporting.InvalidError(self._meta.country, self._meta.site, siteId)

    def extract_ad(self, soup, siteId=None):
        # A dictionnary of every saved value
        values = dict()
        # A field is an instance of Field
        for (name, field) in self.get_fields():
            # Save the field value extracted from the soup (or from the other values)
            value = field.extract(soup, values)
            # This field might be required
            if value is None and field.required:
                # Exception at a field level
                raise field.exception(self._meta.country, self._meta.site, siteId)
            # Prepare the value to be saved
            values[name] = self.prepare(name, value)
        return values
