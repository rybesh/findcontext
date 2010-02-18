from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from api.handlers import ResourceHandler, PackageHandler, LogRecordHandler

class ResourcesResource(Resource):
    def determine_emitter(self, request, *args, **kwargs):
        if len(kwargs) == 0: # no id specified
            default = 'atom'
        else: 
            default = 'osd'
        return request.GET.get('format', default)

class PackagesResource(Resource):
    def determine_emitter(self, request, *args, **kwargs):
        if len(kwargs) == 0: # no id specified
            default = 'json'
        else: 
            default = 'atom'
        return request.GET.get('format', default)

resources = ResourcesResource(
    ResourceHandler, authentication=HttpBasicAuthentication())
packages = PackagesResource(
    PackageHandler, authentication=HttpBasicAuthentication())
log = Resource(
    LogRecordHandler, authentication=HttpBasicAuthentication())

urlpatterns = patterns('',
   url(r'^resource/$', resources),
   url(r'^resource/(?P<id>[^/]+)$', resources),
   url(r'^package/$', packages),
   url(r'^package/(?P<id>[^/]+)$', packages),
   url(r'^log/$', log),
)

