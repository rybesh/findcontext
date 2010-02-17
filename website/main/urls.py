from django.conf.urls.defaults import *
from main.views import sidebar

urlpatterns = patterns('',
   url(r'^sidebar$', sidebar),
)

