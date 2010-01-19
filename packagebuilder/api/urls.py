from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from packagebuilder.api.handlers import ResourceHandler

resource_handler = Resource(
    ResourceHandler, authentication=HttpBasicAuthentication())

urlpatterns = patterns('',
   url(r'^resource/$', resource_handler),
   url(r'^resource/(?P<id>[^/]+)/$', resource_handler),
)

