from django.conf.urls.defaults import *
from views import index, install, jetpack, sidebar

urlpatterns = patterns('',
   url(r'^/$', index),
   url(r'^install/$', install),
   url(r'^install/findcontext.js$', jetpack),
   url(r'^sidebar/$', sidebar),
)

