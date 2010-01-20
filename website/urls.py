from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^api/', include('website.api.urls')),
    #(r'^account/', include('django_authopenid.urls')),
    #(r'^account/', include('registration.backends.default.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^sidebar/', include('website.sidebar.urls')),
)
