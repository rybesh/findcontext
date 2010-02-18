from django.conf.urls.defaults import *
from main.views import install, jetpack, sidebar

urlpatterns = patterns('',
   url(r'^install/$', install),
   url(r'^install/findcontext.js$', jetpack),
   url(r'^sidebar/$', sidebar),
)

