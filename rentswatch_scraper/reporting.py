# -*- coding: utf-8 -*-
from exceptions import ValueError

import db

dupCount = 0

class ReportError(Exception):
    def __init__(self, country, site, siteId):
        Exception.__init__(self)
        # Register attributes
        self.country = country
        self.site = site
        self.siteId = siteId

    def save(self):
        return report(self.country, self.site, self.siteId, self.name)

class DuplicateError(ReportError):
    def __init__(self, country, site, siteId):
        self.name = 'duplicate'
        global dupCount
        dupCount = dupCount + 1
        ReportError.__init__(self, country, site, siteId)

    def save(self):
        return None

class BogusError(ReportError):
    def __init__(self, country, site, siteId):
        self.name = 'bogus'
        ReportError.__init__(self, country, site, siteId)

# Wrong type is for business premises, garage etc.
class WrongtypeError(ReportError):
    def __init__(self, country, site, siteId):
        self.name = 'wrong-type'
        ReportError.__init__(self, country, site, siteId)

class RentMissingError(ReportError):
    def __init__(self, country, site, siteId):
        self.name = 'rent-missing'
        ReportError.__init__(self, country, site, siteId)

class SpaceMissingError(ReportError):
    def __init__(self, country, site, siteId):
        self.name = 'space-missing'
        ReportError.__init__(self, country, site, siteId)

class TimeoutError(ReportError):
    def __init__(self, country, site, siteId):
        self.name = 'timeout'
        ReportError.__init__(self, country, site, siteId)

class UnreachableError(ReportError):
    def __init__(self, country, site, siteId):
        self.name = 'unreachable'
        ReportError.__init__(self, country, site, siteId)

class InvalidError(ReportError):
    def __init__(self, country, site, siteId):
        self.name = 'invalid'
        ReportError.__init__(self, country, site, siteId)

# To quickly catch all reportable errors
REPORTABLE_ERRORS = (DuplicateError, BogusError, WrongtypeError,
                    SpaceMissingError, RentMissingError, InvalidError,
                    TimeoutError, UnreachableError,)

def report(country, site, siteId, name):
    # Check the validity of the report name
    if not name in db.REPORT_NAMES:
        raise ValueError("'%s' is not a valid name!" % name)
    # DB saving
    return db.Report(
        country=country,
        site=site,
        siteId=siteId,
        name=name
    )
