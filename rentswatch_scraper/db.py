from sqlobject import connectionForURI, sqlhub, SQLObject, sqlbuilder, \
                      BoolCol, StringCol, UnicodeCol, FloatCol, \
                      DateTimeCol, DateCol, DatabaseIndex
import os

# Get DATABASE_URL env variable or use sqlite
DATABASE_URL = os.environ.get('DATABASE_URL', "sqlite://%s" % os.path.abspath("dev.db") )
REPORT_NAMES = ('duplicate', 'bogus', 'rent-missing', 'space-missing',
                'timeout', 'wrong-type', 'unreachable', 'invalid')
# Establish the connection
connection = connectionForURI(DATABASE_URL)
connection.dbEncoding="utf8"

def setup(databaseUrl=DATABASE_URL):
    # Establish the connection
    connection = connectionForURI(databaseUrl)
    connection.dbEncoding="utf8"
    # No pooling
    connection._pool = None
    sqlhub.processConnection = connection
    # Creates tables
    Ad.createTable(ifNotExists=True)
    Report.createTable(ifNotExists=True)


class Ad(SQLObject):
    # "listed" if needs more scraping, "scraped" if it's done
    status = StringCol(length=10, default=None)
    # Name of the website
    site = StringCol(length=30, notNull=True)
    # Date the ad was first scraped
    createdAt = DateTimeCol(default=DateTimeCol.now)
    # The unique ID from the site where it's scrapped from
    siteId = StringCol(length=100, notNull=True)
    # Extra costs (heating mostly)
    serviceCharge = FloatCol(default=None)
    serviceChargeOriginalCurrency = FloatCol(default=None)
    # Base costs (without heating)
    baseRent = FloatCol(default=None)
    baseRentOriginalCurrency = FloatCol(default=None)
    # Total cost
    totalRent = FloatCol(default=None)
    totalRentOriginalCurrency = FloatCol(default=None)
    # Country, 2 letter code
    country = StringCol(length=2, notNull=True)
    # Currency, 3 letter code
    currency = StringCol(length=3, default='EUR')
    # Surface in square meters
    livingSpace = FloatCol(default=None)
    # Price per square meter
    pricePerSqm = FloatCol(default=None)
    # True if the flat or house is furnished
    furnished = BoolCol(default=None)
    # y if realtor, n if rented by a physical person
    realtor = BoolCol(default=None)
    # The name of the realtor or person offering the flat
    realtorName = UnicodeCol(length=300, dbEncoding='utf8', default=None)
    # Latitude
    latitude = FloatCol(default=None)
    # Longitude
    longitude = FloatCol(default=None)
    # "y" if there is a balcony/terrasse
    balcony = BoolCol(default=None)
    # The year the building was built
    yearConstructed = StringCol(length=100, dbEncoding='utf8', default=None)
    # "y" if the flat comes with a cellar
    cellar = BoolCol(default=None)
    # "y" if the flat comes with a parking or a garage
    parking = BoolCol(default=None)
    # House Number in the street
    houseNumber = StringCol(length=100, dbEncoding='utf8', default=None)
    # Street name (incl. "street")
    street = StringCol(length=1000, dbEncoding='utf8', default=None)
    # zip code
    zipCode = StringCol(length=100, default=None)
    # City
    city = UnicodeCol(length=100, dbEncoding='utf8', default=None)
    # y if a lift is present
    lift = BoolCol(default=None)
    # Type of flat (no typology)
    typeOfFlat = StringCol(length=100, default=None)
    # Number of rooms
    noRooms = StringCol(length=10, default=None)
    # Floor the flat is at
    floor = StringCol(length=100, default=None)
    # y if there is a garden
    garden = BoolCol(default=None)
    # y if the flat is wheelchair accessible
    barrierFree = BoolCol(default=None)
    # Country, 2 letter code
    country = StringCol(length=2, default=None)
    # URL of the page
    sourceUrl = StringCol(length=1000, default=None)
    # URL of the page
    description = StringCol(default=None)
    # An ad must be unique on the website
    adIndex = DatabaseIndex('siteId', 'site', unique=True)

class Rent(SQLObject):
    # Total cost
    totalRent = FloatCol(default=None)
    # Surface in square meters
    livingSpace = FloatCol(default=None)
    # Currency, 3 letter code
    currency = StringCol(length=3, default='EUR')
    # Date of arrival
    moveIn = DateCol(default=None)
    # IP of the user hashed
    ipHash = StringCol(length=512,default=None)
    # Date of creating
    createdAt = DateTimeCol(default=DateTimeCol.now)

class Report(SQLObject):
    createdAt = DateTimeCol(default=DateTimeCol.now)                            # Date the ad was first scraped
    country = StringCol(length=2, default=None)                                 # Country, 2 letter code
    site = StringCol(length=30, default=None)                                   # Name of the website
    siteId = StringCol(length=100, default=None)                                # The unique ID from the site where it's scrapped from
    name = StringCol(length=100, default=None)                                  # Name of the report: duplicate, bogus, rent-missing, space-missing, timeout
