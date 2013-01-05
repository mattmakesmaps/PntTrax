from django.conf.urls import patterns, include, url
from GPSTracker.models import Client, Group, Report

# Uncomment the next two lines to enable the admin:
from django.contrib.gis import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^gpstracker/', include('GPSTracker.urls', namespace='GPSTracker')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

)
