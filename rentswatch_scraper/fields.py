from .browser import regex as fast_regex

import itertools
import abc
import reporting

class Field(object):
    __metaclass__ = abc.ABCMeta
    _counter = itertools.count()

    def __init__(self, required=False, exception=reporting.BogusError):
        self.required  = required
        self.exception = exception
        # Preserve field order
        self._count = Field._counter.next()

    @abc.abstractmethod
    def extract(self, soup, values):
        return None

class RegexField(Field):

    def __init__(self, selector=None, regex=None, transform=None, html=False,
                required=False, exception=reporting.BogusError):
        self.selector  = selector
        self.regex     = regex
        self.transform = transform
        self.html      = html
        # Call parent constructor
        super(RegexField, self).__init__(required, exception)

    def extract(self, soup, values):
        # Parse page HTML using a selector
        if self.selector is not None:
            # Extract the element containing
            element = soup.select_one(self.selector)
            # Element not found
            if element is None: return None
        # No selector provided the soup might be just text
        else: element = soup
        # Should we extract value as html or text?
        value = element if self.html else element.text.encode('utf-8')
        # Should we apply a regex to extract the value
        value = value if self.regex is None else fast_regex(self.regex, value)
        # Strip extracted values
        value = value.strip() if isinstance(value, str) else value
        # Should we transform the value afterward?
        if hasattr(self.transform, '__call__')  and value is not None:
            # Transforms the value
            value = self.transform(value)
        return value

class AttributeField(Field):

    def __init__(self, selector='a', name='name', transform=None,
                required=False, exception=reporting.BogusError):
        self.selector  = selector
        self.name      = name
        self.transform = transform
        # Call parent constructor
        super(AttributeField, self).__init__(required, exception)

    def extract(self, soup, values):
        # Parse page HTML using a selector
        if self.selector is not None:
            # Extract the element containing
            element = soup.select_one(self.selector)
            # Element not found
            if element is None: return None
        # No selector provided the soup might be just text
        else: element = soup
        # Get the value from the attributes of the element
        try: 
            value = element[self.name]
        # There is no such key in the element
        except KeyError:
            value = None
        # Should we transform the value afterward?
        if hasattr(self.transform, '__call__')  and value is not None:
            # Transforms the value
            value = self.transform(value)
        return value

class ComputedField(Field):
    def __init__(self, fn, required=False, exception=reporting.BogusError):
        # The function called to cumputte this field
        self.fn = fn
        # Call parent constructor
        super(ComputedField, self).__init__(required, exception)
    # The extract method just return the result of the computation function
    def extract(self, soup, values): return self.fn(soup, values)
