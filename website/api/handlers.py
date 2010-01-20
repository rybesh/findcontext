from api.emitters import OSDEmitter, AtomEmitter, CustomJSONEmitter
from django import forms
from django.http import HttpResponse
from lxml import etree
from main.models import Resource, Package
from piston.emitters import Emitter, Mimer
from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc

osd_schema = etree.RelaxNG(file='schemas/opensearchdescription.rng')

class AnonymousResourceHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    model = Resource

class ResourceHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'DELETE')
    model = Resource
    anonymous = AnonymousResourceHandler
    def bad_request(self, message):
        return HttpResponse('Bad Request: %s' % message, status=400)

    def create(self, request, *args, **kwargs):
        if not request.content_type == 'application/opensearchdescription+xml':
            return self.bad_request(
                'Content-Type must be application/opensearchdescription+xml')
        try:
            osd_schema.assertValid(request.data)
        except etree.DocumentInvalid as e:
            return self.bad_request(e.message)
        short_name = request.data.find(
            '{http://a9.com/-/spec/opensearch/1.1/}ShortName').text
        if Resource.objects.filter(_short_name__exact=short_name).count() > 0:
            return rc.DUPLICATE_ENTRY
        else:
            Resource.objects.create(open_search_description=request.data)
            return rc.CREATED

class AnonymousPackageHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    model = Package

class PackageHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Package
    anonymous = AnonymousPackageHandler

Emitter.register('osd', OSDEmitter, 'application/opensearchdescription+xml; charset=utf-8')
Emitter.register('atom', AtomEmitter, 'application/atom+xml; charset=utf-8')
Emitter.register('json', CustomJSONEmitter, 'application/json; charset=utf-8')

def load_xml(raw_post_data):
    try:
        return etree.fromstring(raw_post_data)
    except etree.XMLSyntaxError:
        raise ValueError

Mimer.register(load_xml, ('application/opensearchdescription+xml',))

        
