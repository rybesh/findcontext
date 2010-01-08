from piston.handler import BaseHandler
from main.models import Resource, Package

class ResourceHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Resource

from piston.emitters import Emitter
from api.emitters import CustomXMLEmitter, CustomJSONEmitter

Emitter.register('xml', CustomXMLEmitter, 'text/xml; charset=utf-8')
Emitter.register('json', CustomJSONEmitter, 'application/json; charset=utf-8')

        
