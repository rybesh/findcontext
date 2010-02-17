import json
import copy
import textwrap
from urlparse import urlparse
from django.http import HttpRequest
from django.shortcuts import render_to_response
from django.core.urlresolvers import resolve
from main import uri_template

def _load_json(request, uri):
    view, args, kwargs = resolve(urlparse(uri)[2])
    GET = copy.copy(request.GET)
    GET['format'] = 'json'
    request.GET = GET
    kwargs['request'] = request
    return json.loads(view(*args, **kwargs).content)    

def sidebar(request):
    package_uri = request.GET.get('p')
    query = request.GET.get('q', '')
    o = _load_json(request, package_uri)
    entries = o['feed']['entry']
    resources = []
    for e in entries:
        r = {}
        osd = e['content']['OpenSearchDescription']
        template = osd['Url']['template']
        r['query_uri'] = uri_template.sub(template, { 'searchTerms': query });
        r['name'] = osd['ShortName']['$t']
        r['description'] = textwrap.wrap(osd['Description']['$t'], 43)
        resources.append(r)
    info = { 'height': 60 }
    button = { 'width': 240, 'height': 25, 'spacing': 31 }
    height = button['spacing'] * len(resources) + info['height'] + 5
    return render_to_response('index.svg', { 
            'query': query, 'resources': resources,
            'height': height, 'button': button, 'info': info },
                              mimetype='image/svg+xml')
