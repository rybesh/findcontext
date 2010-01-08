__test__ = {"doctest": """

# Put a resource in the database.
>>> from lxml import etree
>>> from main.models import Resource
>>> osd = etree.parse('main/test/wikipedia.xml')
>>> r = Resource.objects.create(open_search_description=osd.getroot())
>>> r.save()

>>> from django.test.client import Client
>>> c = Client()

# Test anonymously getting the resource as XML.
>>> response = c.get('/api/resource/%s/?format=xml' % r.id)
>>> print response.content # doctest: +REPORT_NDIFF
<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/" xmlns:moz="http://www.mozilla.org/2006/browser/search/">
  <!-- Created on Wed, 07 Jan 2009 02:25:05 GMT -->
  <ShortName>Wikipedia (en) - Go</ShortName>
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
      "$t": "Wikipedia (en) - Go"
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
"""}

