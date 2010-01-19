# -*- coding: utf-8 -*-
import unittest
import difflib
import json
import base64
import feedvalidator
from lxml import etree
from StringIO import StringIO
from django.test.client import Client
from django.contrib.auth.models import User
from django.utils import feedgenerator
from main.models import Resource, Package


class TestCase(unittest.TestCase):
     def assert_equal_show_diff(self, a, b):
        self.assertEqual(a, b, '\n' + ''.join(difflib.ndiff(a.splitlines(True), 
                                                            b.splitlines(True))))

class ResourceTestCase(TestCase):

    def setUp(self):
        self.c = Client()
        self.r = Resource.objects.create(
            open_search_description=etree.parse(
                'test-data/wikipedia.xml').getroot())
        self.u = User.objects.create_user('tester', '', 'testerpass')

    def tearDown(self):
        self.r.delete()
        self.u.delete()

    def test_get_resource_as_xml(self):
        response = self.c.get('/api/resource/%s' % self.r.id)
        expected = u'''<?xml version='1.0' encoding='utf-8'?>
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
'''.encode('utf-8')
        self.assertEqual('application/opensearchdescription+xml; charset=utf-8',
                         response['Content-Type'])
        self.assertEqual(200, response.status_code)
        self.assert_equal_show_diff(expected, response.content)
        
    def test_get_resource_as_json(self):
        response = self.c.get('/api/resource/%s?format=json' % self.r.id)
        expected = '''{
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
}'''
        self.assertEqual('application/json; charset=utf-8',
                         response['Content-Type'])
        self.assertEqual(200, response.status_code)
        self.assert_equal_show_diff(expected, 
                                    json.dumps(json.loads(response.content), 
                                               sort_keys=True, indent=2))

    def test_post_resource_anonymously(self):
        response = self.c.post(
            '/api/resource/', 
            data=open('test-data/worldcat.xml').read(),
            content_type='application/opensearchdescription+xml')
        self.assertEqual(401, response.status_code)
        self.assertEqual('Authorization Required', response.content)

    def test_post_resource_authenticated(self):
        response = self.c.post(
            '/api/resource/', 
            data=open('test-data/worldcat.xml').read(), 
            content_type='application/opensearchdescription+xml', 
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass'))
        self.assertEqual(201, response.status_code)
        self.assertEqual('Created', response.content)

    def test_post_resource_wrong_content_type(self):
        response = self.c.post(
            '/api/resource/', 
            data=open('test-data/worldcat.xml').read(), 
            content_type='text/xml',
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass'))
        self.assertEqual(400, response.status_code)
        self.assertEqual('Bad Request: Content-Type must be application/opensearchdescription+xml', 
                         response.content)

    def test_post_resource_duplicate_shortname(self):
        response = self.c.post(
            '/api/resource/', 
            data=open('test-data/wikipedia.xml').read(), 
            content_type='application/opensearchdescription+xml', 
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass'))
        self.assertEqual(409, response.status_code)
        self.assertEqual('Conflict/Duplicate', response.content)

    def test_post_resource_invalid_xml(self):
        response = self.c.post(
            '/api/resource/', 
            data=open('test-data/not-an-opensearch-desc.xml').read(), 
            content_type='application/opensearchdescription+xml', 
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass'))
        self.assertEqual(400, response.status_code)
        self.assertEqual('Bad Request: Expecting element OpenSearchDescription, got foo, line 1',
                         response.content)

    def test_post_resource_nonxml(self):
        response = self.c.post(
            '/api/resource/', 
            data='This is not XML',
            content_type='application/opensearchdescription+xml', 
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass'))
        self.assertEqual(400, response.status_code)
        self.assertEqual('Bad Request', response.content)

    def test_post_resource_nothing(self):
        response = self.c.post(
            '/api/resource/', 
            content_type='application/opensearchdescription+xml', 
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass'))
        self.assertEqual(400, response.status_code)
        self.assertEqual('Bad Request', response.content)


class PackageTestCase(TestCase):

    def setUp(self):
        self.c = Client()
        self.u = User.objects.create_user('tester', '', 'testerpass')
        self.p = Package.objects.create(name='Test Package', description='This is a test.', owner=self.u)
        self.p.resources.add(Resource.get('Celtic Art & Cultures'))
        self.p.resources.add(Resource.get('Monasticon Hibernicum'))
        self.p.save()

    def tearDown(self):
        self.p.delete()
        self.u.delete()

    def test_get_package_as_xml(self):
        response = self.c.get('/api/package/%s' % self.p.id)
        expected = '''<?xml version='1.0' encoding='utf-8'?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Test Package</title>
  <id>http://findcontext.org/api/package/{package_id}</id>
  <updated>{package_updated}</updated>
  <subtitle>This is a test.</subtitle>
  <entry>
    <title>Monasticon Hibernicum</title>
    <id>http://findcontext.org/api/resource/1</id>
    <updated>2010-01-19T00:18:34Z</updated>
    <summary>Early Christian ecclesiastical settlement in Ireland, 5th to 12th centuries.</summary>
    <author>
      <name>Ryan Shaw</name>
    </author>
    <content type="application/opensearchdescription+xml">
      <OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/">
  <ShortName>Monasticon Hibernicum</ShortName>
  <Description>Early Christian ecclesiastical settlement in Ireland, 5th to 12th centuries.</Description>
  <Url method="get" template="http://www.google.com/search?tbo=1&amp;tbs=tl:1&amp;q=site:monasticon.celt.dias.ie+{{searchTerms}}" type="text/html"/>
  <Developer>Ryan Shaw</Developer>
  <InputEncoding>UTF-8</InputEncoding>
</OpenSearchDescription>
    </content>
  </entry>
  <entry>
    <title>Celtic Art &amp; Cultures</title>
    <id>http://findcontext.org/api/resource/12</id>
    <updated>2010-01-19T00:18:35Z</updated>
    <summary>Images of Celtic art, artifacts, and architecture.</summary>
    <author>
      <name>Ryan Shaw</name>
    </author>
    <content type="application/opensearchdescription+xml">
      <OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/">
  <ShortName>Celtic Art &amp; Cultures</ShortName>
  <Description>Images of Celtic art, artifacts, and architecture.</Description>
  <Url method="get" template="http://www.google.com/search?tbo=1&amp;tbs=tl:1&amp;q=site:www.unc.edu/celtic+{{searchTerms}}" type="text/html"/>
  <Developer>Ryan Shaw</Developer>
  <InputEncoding>UTF-8</InputEncoding>
</OpenSearchDescription>
    </content>
  </entry>
</feed>
'''.format(package_id=self.p.id, 
                  package_updated=feedgenerator.rfc3339_date(self.p.last_updated))
        self.assertEqual('application/atom+xml; charset=utf-8', 
                         response['Content-Type'])
        self.assertEqual(200, response.status_code)
        self.assert_equal_show_diff(expected, response.content)
        # Validate Atom feed
        try:
            events = feedvalidator.validateString(
                response.content, firstOccurrenceOnly=True)['loggedEvents']
        except feedvalidator.logging.ValidationFailure as e:
            events = [e.event]
        from feedvalidator import compatibility
        #events = compatibility.AA(events)
        events = compatibility.A(events)
        from feedvalidator.formatter.text_plain import Formatter
        output = Formatter(events)
        if output:
            self.fail('\n'.join(output))
            
