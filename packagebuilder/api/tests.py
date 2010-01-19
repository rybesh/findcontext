# -*- coding: utf-8 -*-
__test__ = {"doctest": u"""

# Put a resource in the database.
>>> from lxml import etree
>>> from main.models import Resource
>>> osd = etree.parse('test-data/wikipedia.xml')
>>> r = Resource.objects.create(open_search_description=osd.getroot())

>>> from django.test.client import Client
>>> c = Client()

# Test anonymously getting the resource as XML.
>>> response = c.get('/api/resource/%s/?format=xml' % r.id)
>>> print response.content.decode('utf-8') # doctest: +REPORT_NDIFF
<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/" xmlns:moz="http://www.mozilla.org/2006/browser/search/">
  <!-- Created on Wed, 07 Jan 2009 02:25:05 GMT -->
  <ShortName>ウィキペディア（英語）</ShortName>
  <Description>Wikipedia, the free encyclopedia</Description>
  <Url method="get" template="http://en.wikipedia.org/wiki/Special:Search?search={searchTerms}&amp;go=Go" type="text/html"/>
  <Url template="http://en.wikipedia.org/w/api.php?action=opensearch&amp;search={searchTerms}" type="application/x-suggestions+json"/>
  <Contact>rocksoccer2004@gmail.com</Contact>
  <Image height="16" width="16">http://mycroft.mozdev.org/updateos.php/id0/wikipedia.ico</Image>
  <Developer>rocksoccer</Developer>
  <InputEncoding>UTF-8</InputEncoding>
  <moz:SearchForm>http://en.wikipedia.org</moz:SearchForm>
  <moz:UpdateUrl>http://mycroft.mozdev.org/updateos.php/id0/wikipedia.xml</moz:UpdateUrl>
  <moz:IconUpdateUrl>http://mycroft.mozdev.org/updateos.php/id0/wikipedia.ico</moz:IconUpdateUrl>
  <moz:UpdateInterval>7</moz:UpdateInterval>
</OpenSearchDescription>
<BLANKLINE>

# Test anonymously getting the resource as JSON.
>>> import json
>>> response = c.get('/api/resource/%s/?format=json' % r.id)
>>> print json.dumps(json.loads(response.content), sort_keys=True, indent=2) # doctest: +REPORT_NDIFF
{
  "OpenSearchDescription": {
    "Contact": {
      "$t": "rocksoccer2004@gmail.com"
    }, 
    "Description": {
      "$t": "Wikipedia, the free encyclopedia"
    }, 
    "Developer": {
      "$t": "rocksoccer"
    }, 
    "Image": {
      "$t": "http://mycroft.mozdev.org/updateos.php/id0/wikipedia.ico", 
      "height": "16", 
      "width": "16"
    }, 
    "InputEncoding": {
      "$t": "UTF-8"
    }, 
    "ShortName": {
      "$t": "\u30a6\u30a3\u30ad\u30da\u30c7\u30a3\u30a2\uff08\u82f1\u8a9e\uff09"
    }, 
    "Url": [
      {
        "method": "get", 
        "template": "http://en.wikipedia.org/wiki/Special:Search?search={searchTerms}&go=Go", 
        "type": "text/html"
      }, 
      {
        "template": "http://en.wikipedia.org/w/api.php?action=opensearch&search={searchTerms}", 
        "type": "application/x-suggestions+json"
      }
    ], 
    "moz$IconUpdateUrl": {
      "$t": "http://mycroft.mozdev.org/updateos.php/id0/wikipedia.ico"
    }, 
    "moz$SearchForm": {
      "$t": "http://en.wikipedia.org"
    }, 
    "moz$UpdateInterval": {
      "$t": "7"
    }, 
    "moz$UpdateUrl": {
      "$t": "http://mycroft.mozdev.org/updateos.php/id0/wikipedia.xml"
    }, 
    "xmlns": "http://a9.com/-/spec/opensearch/1.1/", 
    "xmlns$moz": "http://www.mozilla.org/2006/browser/search/"
  }
}

# Test anonymously POSTing a new resource (which should fail).
>>> xml = open('test-data/worldcat.xml').read()
>>> response = c.post('/api/resource/', data=xml, content_type='text/xml') 
>>> print response.content
Authorization Required

# Test authenticated POSTing of a new resource.
>>> from django.contrib.auth.models import User
>>> import base64
>>> User.objects.create_user('tester', '', 'testerpass').save()
>>> response = c.post('/api/resource/', data=xml, content_type='text/xml', 
...            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass')) 
>>> print response.content
Created
>>> Resource.get('WorldCat Catalog: Books')
<Resource: WorldCat Catalog: Books>

# Test POSTing an OpenSearch description with a duplicate ShortName.
>>> response = c.post('/api/resource/', data=xml, content_type='text/xml', 
...            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass')) 
>>> print response.content
Conflict/Duplicate

# Test POSTing invalid OpenSearch description XML.
>>> xml = open('test-data/not-an-opensearch-desc.xml').read()
>>> response = c.post('/api/resource/', data=xml, content_type='text/xml', 
...            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass')) 
>>> print response.content
Expecting element OpenSearchDescription, got foo, line 1

# Test POSTing non-XML.
>>> response = c.post('/api/resource/', data='This is not XML.', content_type='text/xml', 
...            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass')) 
>>> print response.content
Bad Request

# Test POSTing nothing.
>>> response = c.post('/api/resource/', content_type='text/xml', 
...            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass')) 
>>> print response.content
Bad Request

"""}

