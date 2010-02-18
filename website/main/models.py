# -*- coding: utf-8 -*-

from django import forms
from django.db import models, transaction
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
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
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(ElementField, self).formfield(**defaults)

class Resource(models.Model):
    u"""
    A resource described by an OpenSearch description document.

    >>> osd = etree.parse('test-data/wikipedia.xml')
    >>> r = Resource(open_search_description=osd.getroot())

    # Element text values in the default namespace can be accessed as attributes
    >>> print r.short_name
    ウィキペディア（英語）
    >>> print r.description
    Wikipedia, the free encyclopedia
    >>> r.doesnotexist
    Traceback (most recent call last):
    ...
    AttributeError: 'Resource' object has no attribute 'doesnotexist'

    # Attributes other than open_search_description are not settable
    # (Later we'll change this to update the underlying XML.)
    >>> r.short_name = 'foobar'
    Traceback (most recent call last):
    ...
    AttributeError: 'short_name' attribute on 'Resource' object is read-only

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

    # Private _short_name field gets set (from the XML) on save:
    >>> print r._short_name
    <BLANKLINE>
    >>> r.save()
    >>> print r._short_name
    ウィキペディア（英語）

    # Can't have two resources with the same short name
    >>> r2 = Resource(open_search_description=osd.getroot())
    >>> r2.save()
    Traceback (most recent call last):
    ...
    IntegrityError: duplicate key value violates unique constraint "main_resource_short_name_key"
    <BLANKLINE>
    >>> transaction.rollback()

    # Do lookups using Resource.get(short_name)
    >>> osd = etree.parse('test-data/worldcat.xml')
    >>> Resource.objects.create(open_search_description=osd.getroot())
    <Resource: WorldCat Catalog: Books>
    >>> r3 = Resource.get('WorldCat Catalog: Books')
    >>> print r3.description
    Search Open WorldCat Catalog for Books

    # Clean up
    >>> r.delete()
    >>> r3.delete()
    """
    open_search_description = ElementField()
    _short_name = models.CharField(max_length=36, unique=True, editable=False, db_column='short_name')
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    _derived_attributes = set()
    @classmethod
    def get(cls, short_name):
        return Resource.objects.get(_short_name__exact=short_name)
    def get_open_search_value(self, ns, key):
        child = self.open_search_description.find('{%s}%s' % (ns, key))
        if child is None:
            return None
        return child.text
    def save(self, *args, **kwargs):
        self._short_name = self.short_name
        super(Resource, self).save(*args, **kwargs)
    def get_absolute_url(self):
        return '/api/resource/%i' % self.id
    def _get_uri(self):
        return 'http://%s%s' % (Site.objects.get_current().domain,
                                self.get_absolute_url())
    uri = property(_get_uri)
    def __getattr__(self, key):
        camel_key = ''.join([ s.capitalize() for s in key.split('_') ])
        value = self.get_open_search_value(
            'http://a9.com/-/spec/opensearch/1.1/', camel_key)
        if value is None:
            raise AttributeError("'Resource' object has no attribute '%s'" % key)
        self._derived_attributes.add(key)
        return value
    def __setattr__(self, key, value):
        if key in self._derived_attributes:
            raise AttributeError("'%s' attribute on 'Resource' object is read-only" % key)
        super(Resource, self).__setattr__(key, value)
    def __unicode__(self):
        return self.short_name

class Package(models.Model):
    name = models.CharField(max_length=40, unique=True)
    description = models.TextField()
    owner = models.ForeignKey(User)
    resources = models.ManyToManyField(Resource)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    def get_absolute_url(self):
        return '/api/package/%i' % self.id
    def _get_uri(self):
        return 'http://%s%s' % (Site.objects.get_current().domain,
                                self.get_absolute_url())
    uri = property(_get_uri)
    def __unicode__(self):
        return self.name

class LogRecord(models.Model):
    user = models.ForeignKey(User, related_name='log')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '[%s] %s' % (self.timestamp, self.user.username)
    class Meta:
        ordering = ['-timestamp']
