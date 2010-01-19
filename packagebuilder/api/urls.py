from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from packagebuilder.api.handlers import ResourceHandler, PackageHandler

class ResourceResource(Resource):
    def determine_emitter(self, request, *args, **kwargs):
        return request.GET.get('format', 'osd')

class PackageResource(Resource):
    def determine_emitter(self, request, *args, **kwargs):
        return request.GET.get('format', 'atom')

resources = ResourceResource(
    ResourceHandler, authentication=HttpBasicAuthentication())
packages = PackageResource(
    PackageHandler, authentication=HttpBasicAuthentication())

urlpatterns = patterns('',
   url(r'^resource/$', resources),
   url(r'^resource/(?P<id>[^/]+)$', resources),
   url(r'^package/(?P<id>[^/]+)$', packages),
)

