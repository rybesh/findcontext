from api.emitters import CustomXMLEmitter, CustomJSONEmitter
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
    def create(self, request, *args, **kwargs):
        try:
            osd_schema.assertValid(request.data)
        except etree.DocumentInvalid as e:
            return HttpResponse(e.message, status=400)
        short_name = request.data.find(
            '{http://a9.com/-/spec/opensearch/1.1/}ShortName').text
        if Resource.objects.filter(_short_name__exact=short_name).count() > 0:
            return rc.DUPLICATE_ENTRY
        else:
            Resource.objects.create(open_search_description=request.data)
            return rc.CREATED

Emitter.register('xml', CustomXMLEmitter, 'text/xml; charset=utf-8')
Emitter.register('json', CustomJSONEmitter, 'application/json; charset=utf-8')

def load_xml(raw_post_data):
    try:
        return etree.fromstring(raw_post_data)
    except etree.XMLSyntaxError:
        raise ValueError

Mimer.unregister(Mimer(None).loader_for_type('text/xml'))
Mimer.register(load_xml, ('text/xml',))

        
