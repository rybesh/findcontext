from django.conf.urls.defaults import *
from sidebar.views import index

urlpatterns = patterns('',
   url(r'^(?P<pkg>.+)$', index),
)

