from sqlobject import connectionForURI, sqlhub, SQLObject, sqlbuilder, \
                      BoolCol, StringCol, UnicodeCol, FloatCol, \
                      DateTimeCol, DatabaseIndex
import os

# Get DATABASE_URL env variable or use sqlite
DATABASE_URL = os.environ.get('DATABASE_URL', "sqlite://%s" % os.path.abspath("dev.db") )
REPORT_NAMES = ('duplicate', 'bogus', 'rent-missing', 'space-missing', 'timeout', 'wrong-type')
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
    status = StringCol(length=10, default=None)                                 # "listed" if needs more scraping, "scraped" if it's done
    site = StringCol(length=30, default=None)                                   # Name of the website
    createdAt = DateTimeCol(default=DateTimeCol.now)                            # Date the ad was first scraped
    siteId = StringCol(length=100, default=None)                                # The unique ID from the site where it's scrapped from
    serviceCharge = FloatCol(default=None)                                      # Extra costs (heating mostly)
    baseRent = FloatCol(default=None)                                           # Base costs (without heating)
    totalRent = FloatCol(default=None)                                          # Total cost
    livingSpace = FloatCol(default=None)                                        # Surface in square meters
    pricePerSqm = FloatCol(default=None)                                        # Price per square meter
    furnished = BoolCol(default=None)                                           # True if the flat or house is furnished
    realtor = BoolCol(default=None)                                             # y if realtor, n if rented by a physical person
    realtorName = UnicodeCol(length=300, dbEncoding='utf8', default=None)       # The name of the realtor or person offering the flat
    latitude = FloatCol(default=None)                                           # Latitude
    longitude = FloatCol(default=None)                                          # Longitude
    balcony = BoolCol(default=None)                                             # "y" if there is a balcony/terrasse
    yearConstructed = StringCol(length=100, dbEncoding='utf8', default=None)    # The year the building was built
    cellar = BoolCol(default=None)                                              # "y" if the flat comes with a cellar
    parking = BoolCol(default=None)                                             # "y" if the flat comes with a parking or a garage
    houseNumber = StringCol(length=100, dbEncoding='utf8', default=None)        # House Number in the street
    street = StringCol(length=1000, dbEncoding='utf8', default=None)            # Street name (incl. "street")
    zipCode = StringCol(length=100, default=None)                               # zip code
    city = UnicodeCol(length=100, dbEncoding='utf8', default=None)              # City
    lift = BoolCol(default=None)                                                # y if a lift is present
    typeOfFlat = StringCol(length=100, default=None)                            # Type of flat (no typology)
    noRooms = StringCol(length=10, default=None)                                # Number of rooms
    floor = StringCol(length=100, default=None)                                 # Floor the flat is at
    garden = BoolCol(default=None)                                              # y if there is a garden
    barrierFree = BoolCol(default=None)                                         # y if the flat is wheelchair accessible
    country = StringCol(length=2, default=None)                                 # Country, 2 letter code
    sourceUrl = StringCol(length=1000, default=None)                            # URL of the page
    adIndex = DatabaseIndex('siteId', 'site', unique=True)                      # An ad must be unique on the website

class Report(SQLObject):
    createdAt = DateTimeCol(default=DateTimeCol.now)                            # Date the ad was first scraped
    country = StringCol(length=2, default=None)                                 # Country, 2 letter code
    site = StringCol(length=30, default=None)                                   # Name of the website
    siteId = StringCol(length=100, default=None)                                # The unique ID from the site where it's scrapped from
    name = StringCol(length=100, default=None)                                  # Name of the report: duplicate, bogus, rent-missing, space-missing, timeout
