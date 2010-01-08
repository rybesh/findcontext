from django.conf.urls.defaults import *
from piston.resource import Resource
from packagebuilder.api.handlers import ResourceHandler

urlpatterns = patterns('',
   url(r'^resource/(?P<id>[^/]+)/', Resource(ResourceHandler)),
)

