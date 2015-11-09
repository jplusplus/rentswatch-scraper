Rentswatch Scraper Framework
============================

This package provides an easy and maintenable way to build a
Rentswatch's scraper. Rentswatch is a cross-borders investigation aiming
to collect data around flat renting in Europe. Its scrapers mainly focus
on adverts.

How to install
--------------

Install using ``pip``...

::

    pip install rentswatch-scraper

How to use
----------

Let's take a look at a quick example of using Rentswatch Scraper to
build a simple model-backed scraper to collect data from a website.

First, you may import the package components to build your scraper:

.. code:: python

    #!/usr/bin/env python
    from rentswatch_scraper.scraper import Scraper
    from rentswatch_scraper.browser import geocode, convert
    from rentswatch_scraper.fields import RegexField, ComputedField
    from rentswatch_scraper import reporting

To factorize as much code as possible we created an abstract class that
every scraper will implement. For the sake of simplicity we'll use a
*dummy website* as follow:

.. code:: python

    class DummyScraper(Scraper):
        # Those are the basic meta-properties that define the scraper behavior
        class Meta:
            country         = 'FR'
            site            = "dummy"
            baseUrl         = 'http://dummy.io'
            listUrl         = baseUrl + '/rent/city/paris/list.php'
            adBlockSelector = '.ad-page-link'

Without any further configuration, this scraper will start to collect
ads from the list page of ``dummy.io``. To find links to the ads, it
will use the CSS selector ``.ad-page-link`` to get ``<a>`` markups and
follow their ``href`` attributes.

We have now to teach the scraper how to extract key figures from the ad
page.

.. code:: python

    class DummyScraper(Scraper):
        # HEADS UP: Meta declarations are hidden here
        # ...
        # ...

        # Extract data using a CSS Selector.
        realtorName = RegexField('.realtor-title')
        # Extract data using a CSS Selector and a Regex.
        serviceCharge = RegexField('.description-list', 'charges : (.*)\s€')
        # Extract data using a CSS Selector and a Regex.
        # This will throw a custom exception if the field is missing.
        livingSpace = RegexField('.description-list', 'surface :(\d*)', required=True, exception=reporting.SpaceMissingError)
        # Extract the value directly, without using a Regex
        totalRent = RegexField('.description-price', required=True, exception=reporting.RentMissingError)
        # Store this value as a private property (begining with a underscore).
        # It won't be saved in the database but it can be helpful as you we'll see.
        _address = RegexField('.description-address')

Every attribute will be saved as a Ad's property, according to the Ad
model.

Some properties may not be extractable from the HTML. You may need to
use a custom function that received existing properties. For this reason
we created a second field type named ``ComputedField``. Since the
properties order of declaration is recorded, we can use previously
declared (and extracted) values to compute new ones.

.. code:: python

    class DummyScraper(Scraper):
        # ...
        # ...

        # Use existing properties `totalRent` and `livingSpace` as they were
        # extracted before this one.
        pricePerSqm = ComputedField(fn=lambda s, values: values["totalRent"] / values["livingSpace"])
        # This full exemple use private properties to find latitude and longitude.
        # To do so we use a buid-in function named `convert` that transforms an
        # address into a dictionary of coordinates.  
        _latLng = ComputedField(fn=lambda s, values: geocode(values['_address'], 'FRA') )
        # Gets a the dictionary field we want.
        latitude = ComputedField(fn=lambda s, values: values['_latLng']['lat'])
        longitude = ComputedField(fn=lambda s, values: values['_latLng']['lng'])

All you need to do now is to create an instance of your class and run
the scraper.

.. code:: python

    # When you script is executed directly
    if __name__ == "__main__":
      dummyScraper = DummyScraper()
      dummyScraper.run()

API Doc
-------

``class`` Scraper
~~~~~~~~~~~~~~~~~

Methods
^^^^^^^

The Scraper class defines a lot of method that we encourage you to
redefine in order to have the full control of your scraper behavior.

+----------------------+------------------------------------------------------------------------------------------------------+
| Name                 | Description                                                                                          |
+======================+======================================================================================================+
| ``extract_ad``       | Extract ads list from a page's soup.                                                                 |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``fail``             | Print out an error message.                                                                          |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``fetch_ad``         | Fetch a single ad page from the target website then create Ad instances by calling ``èxtract_ad``.   |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``fetch_series``     | Fetch a single list page from the target website then fetch an ad by calling ``fetch_ad``.           |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``find_ad_blocks``   | Extract ad block from a page list. Called within ``fetch_series``.                                   |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``get_ad_href``      | Extract a href attribute from an ad block. . Called within ``fetch_series``.                         |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``get_ad_id``        | Extract a siteId from an ad block. Called within ``fetch_series``.                                   |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``get_fields``       | Used internally to generate a list of property to extract from the ad.                               |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``get_series``       | Fetch a list page from the target website.                                                           |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``has_issue``        | True if we met issues with this ad before.                                                           |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``is_scraped``       | True if we already scraped this ad before.                                                           |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``ok``               | Print out an success message.                                                                        |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``prepare``          | Just before saving the values.                                                                       |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``run``              | Run the scrapper.                                                                                    |
+----------------------+------------------------------------------------------------------------------------------------------+
| ``transform_page``   | Transform HTML content of the series page before parsing it.                                         |
+----------------------+------------------------------------------------------------------------------------------------------+

