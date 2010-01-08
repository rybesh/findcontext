from django.db import models
from django.contrib.auth.models import User
from lxml import etree

class ElementField(models.Field):
    description = 'A parsed XML document or fragment'
    __metaclass__ = models.SubfieldBase
    def __init__(self, *args, **kwargs):
        kwargs['editable'] = False
        super(ElementField, self).__init__(*args, **kwargs)
    def db_type(self):
        return 'xml'
    def to_python(self, value):
        if isinstance(value, etree._Element):
            return value
        return etree.fromstring(value)
    def get_db_prep_value(self, value):
        return etree.tostring(value)

class Resource(models.Model):
    """
    A resource described by an OpenSearch description document.

    >>> osd = etree.parse('main/test/wikipedia.xml')
    >>> r = Resource.objects.create(open_search_description=osd.getroot())

    # Element text values in the default namespace can be accessed as attributes
    >>> r.short_name
    'Wikipedia (en) - Go'
    >>> r.description
    'Wikipedia, the free encyclopedia'
    >>> r.doesnotexist
    Traceback (most recent call last):
    ...
    AttributeError: 'Resource' object has no attribute 'doesnotexist'


    # Namespaced element text values can also be accessed easily
    >>> r.get_open_search_value('http://www.mozilla.org/2006/browser/search/', 'SearchForm')
    'http://en.wikipedia.org'
    >>> r.get_open_search_value('doesnotexist', 'doesnotexist')


    # For anything else, use the lxml Element API, e.g.:
    >>> find_urls = etree.ETXPath('{http://a9.com/-/spec/opensearch/1.1/}Url')
    >>> find_urls(r.open_search_description)[0].attrib['method']
    'get'
    >>> find_urls(r.open_search_description)[1].attrib['type']
    'application/x-suggestions+json'
    """
    open_search_description = ElementField()
    def get_open_search_value(self, ns, key):
        child = self.open_search_description.find('{%s}%s' % (ns, key))
        if child is None:
            return None
        return child.text
    def __getattr__(self, key):
        camel_key = ''.join([ s.capitalize() for s in key.split('_') ])
        value = self.get_open_search_value(
            'http://a9.com/-/spec/opensearch/1.1/', camel_key)
        if value is None:
            raise AttributeError("'Resource' object has no attribute '%s'" % key)
        return value

class Package(models.Model):
    name = models.CharField(max_length=40, unique=True)
    description = models.TextField()
    owner = models.ForeignKey(User)
    resources = models.ManyToManyField(Resource)

