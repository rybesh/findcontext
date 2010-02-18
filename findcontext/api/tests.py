# -*- coding: utf-8 -*-
import unittest
import difflib
import json
import base64
import urllib
import feedvalidator
import time
from lxml import etree
from StringIO import StringIO
from django.test.client import Client
from django.contrib.auth.models import User
from django.utils import feedgenerator
from main.models import Resource, Package
from api.utils import TestServerThread


class TestCase(unittest.TestCase):
    def assert_equal_show_diff(self, a, b):
        self.assertEqual(a, b, '\n' + ''.join(difflib.ndiff(a.splitlines(True), 
                                                            b.splitlines(True))))

class LoggingTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.u = User.objects.create_user('tester', '', 'testerpass')

    def tearDown(self):
        self.u.delete()

    def test_anonymous_logging(self):
        response = self.c.post(
            '/api/log/', data='this is a log message', content_type='text/plain')
        self.assertEqual(401, response.status_code)
        self.assertEqual('Authorization Required', response.content)

    def test_empty_log_message(self):
        response = self.c.post(
            '/api/log/', data='', content_type='text/plain',
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass'))
        self.assertEqual(400, response.status_code)
        self.assertEqual('Bad Request: Log message must not be empty', response.content)

    def test_authenticated_logging(self):
        response = self.c.post(
            '/api/log/', data='this is a log message', content_type='text/plain',
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass'))
        self.assertEqual(201, response.status_code)
        self.assertEqual('Created', response.content)
        records = self.u.log.all()
        self.assertEqual(1, len(records))
        self.assertEqual('this is a log message', records[0].message)

    def test_authenticated_logging_with_charset(self):
        response = self.c.post(
            '/api/log/', data='this is a log message', content_type='text/plain; charset=UTF-8',
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('tester:testerpass'))
        self.assertEqual(201, response.status_code)
        self.assertEqual('Created', response.content)
        records = self.u.log.all()
        self.assertEqual(1, len(records))
        self.assertEqual('this is a log message', records[0].message)

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
  <link href="http://findcontext.org/api/package/{package_id}" rel="self"/>
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
  <Url method="get" template="http://www.google.com/search?q=site:monasticon.celt.dias.ie+{{searchTerms}}" type="text/html"/>
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
  <Url method="get" template="http://www.google.com/search?q=site:www.unc.edu/celtic+{{searchTerms}}" type="text/html"/>
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

    def test_get_package_as_json(self):
         response = self.c.get('/api/package/%s?format=json' % self.p.id)
         expected = '''{
  "feed": {
    "entry": [
      {
        "author": {
          "name": {
            "$t": "Ryan Shaw"
          }
        }, 
        "content": {
          "OpenSearchDescription": {
            "Description": {
              "$t": "Early Christian ecclesiastical settlement in Ireland, 5th to 12th centuries."
            }, 
            "Developer": {
              "$t": "Ryan Shaw"
            }, 
            "InputEncoding": {
              "$t": "UTF-8"
            }, 
            "ShortName": {
              "$t": "Monasticon Hibernicum"
            }, 
            "Url": {
              "method": "get", 
              "template": "http://www.google.com/search?q=site:monasticon.celt.dias.ie+{searchTerms}", 
              "type": "text/html"
            }, 
            "xmlns": "http://a9.com/-/spec/opensearch/1.1/"
          }, 
          "type": "application/opensearchdescription+xml"
        }, 
        "id": {
          "$t": "http://findcontext.org/api/resource/1"
        }, 
        "summary": {
          "$t": "Early Christian ecclesiastical settlement in Ireland, 5th to 12th centuries."
        }, 
        "title": {
          "$t": "Monasticon Hibernicum"
        }, 
        "updated": {
          "$t": "2010-01-19T00:18:34Z"
        }
      }, 
      {
        "author": {
          "name": {
            "$t": "Ryan Shaw"
          }
        }, 
        "content": {
          "OpenSearchDescription": {
            "Description": {
              "$t": "Images of Celtic art, artifacts, and architecture."
            }, 
            "Developer": {
              "$t": "Ryan Shaw"
            }, 
            "InputEncoding": {
              "$t": "UTF-8"
            }, 
            "ShortName": {
              "$t": "Celtic Art & Cultures"
            }, 
            "Url": {
              "method": "get", 
              "template": "http://www.google.com/search?q=site:www.unc.edu/celtic+{searchTerms}", 
              "type": "text/html"
            }, 
            "xmlns": "http://a9.com/-/spec/opensearch/1.1/"
          }, 
          "type": "application/opensearchdescription+xml"
        }, 
        "id": {
          "$t": "http://findcontext.org/api/resource/12"
        }, 
        "summary": {
          "$t": "Images of Celtic art, artifacts, and architecture."
        }, 
        "title": {
          "$t": "Celtic Art & Cultures"
        }, 
        "updated": {
          "$t": "2010-01-19T00:18:35Z"
        }
      }
    ], 
    "id": {
      "$t": "http://findcontext.org/api/package/%(package_id)i"
    }, 
    "link": {
      "href": "http://findcontext.org/api/package/%(package_id)i", 
      "rel": "self"
    }, 
    "subtitle": {
      "$t": "This is a test."
    }, 
    "title": {
      "$t": "Test Package"
    }, 
    "updated": {
      "$t": "%(package_updated)s"
    }, 
    "xmlns": "http://www.w3.org/2005/Atom"
  }
}''' % { 'package_id': self.p.id, 
        'package_updated': feedgenerator.rfc3339_date(self.p.last_updated) }
         self.assertEqual('application/json; charset=utf-8', 
                          response['Content-Type'])
         self.assertEqual(200, response.status_code)
         self.assert_equal_show_diff(expected, 
                                     json.dumps(json.loads(response.content), 
                                                sort_keys=True, indent=2))

    def test_get_packages_as_json(self):
         response = self.c.get('/api/package/')
         self.assertEqual('application/json; charset=utf-8', 
                          response['Content-Type'])
         self.assertEqual(200, response.status_code)
         o = json.loads(response.content)
         self.assertEqual(2, len(o))
         self.assertEqual('http://findcontext.org/api/package/1', o[0]['uri'])
         self.assertEqual('Celtic Studies 138', o[0]['name'])
         self.assertEqual('http://findcontext.org/api/package/4', o[1]['uri'])
         self.assertEqual('Test Package', o[1]['name'])


class LiveServerTestCase(unittest.TestCase):

     def setUp(self):
          self.server = TestServerThread('127.0.0.1', 8081)
          self.server.start()

     def tearDown(self):
          self.server.stop()

     def validate_atom(self, url):
          try:
               events = feedvalidator.validateURL(url)['loggedEvents']
          except feedvalidator.logging.ValidationFailure as e:
               events = [e.event]
          # Filter logged events
          from feedvalidator import logging
          events = [ e for e in events if 
                     isinstance(e, logging.Error) or 
                     (isinstance(e, logging.Warning) 
                      and not isinstance(e, logging.DuplicateUpdated)
                      and not isinstance(e, logging.SelfDoesntMatchLocation)) ]
          # Show any remaining events
          from feedvalidator.formatter.text_plain import Formatter
          output = Formatter(events)
          if output: self.fail('\n'.join(output))

     def test_validate_package(self):
          self.validate_atom('http://127.0.0.1:8081/api/package/1')

     def test_validate_all_resources(self):
          self.validate_atom('http://127.0.0.1:8081/api/resource/')
