__author__ = 'matt'
from GPSTracker.models import Client, Group, Report
from django.conf.urls import patterns, url

urlpatterns = patterns('GPSTracker.views',
    # Index
    url(r'^$', 'index'),
    # Root of the client based views
    url(r'^clients/$', 'clients'),
    # Group View
    url(r'^groups/$', 'group'),
    # Group Detail View
    url(r'^groups/(?P<group_id>\d+)/$', 'group_detail'),
)
