from django.shortcuts import render_to_response
from sidebar import uri_template

packages = { 
    'test': { 'name': 'CS 138 Resources',
              'resources': [
            { 'name': 'Wikipedia',
              'description': 'The Free Encyclopedia',
              'template': 'http://en.wikipedia.org/wiki/Special:Search?search={query}' },
            { 'name': 'Melvyl',
              'description': 'The UC Berkeley library catalog',
              'template': 'http://berkeley.worldcat.org/search?q={query}' } ] }
    }

def index(request, pkg):
    package = packages[pkg]
    query_uris = []
    for r in package['resources']:
        r['query_uri'] = uri_template.sub(
            r['template'], { 'query': request.GET.get('q', '') })
    return render_to_response(
        'index.html', 
        { 'resources': package['resources'] }, 
        mimetype='application/xhtml+xml')
