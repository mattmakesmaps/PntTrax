__author__ = 'matt'
from GPSTracker.models import Client, Group, Report, Point, Line, Poly
from django.conf.urls import patterns, url

urlpatterns = patterns('GPSTracker.views',
    # Index
    url(r'^$', 'index'),
    # Root of the client based views
    url(r'^clients/$', 'clients'),
    # About
    url(r'^about/$', 'about'),
    # Group View
    url(r'^groups/$', 'group'),
    # Group Detail View
    url(r'^groups/(?P<group_id>\d+)/$', 'group_detail'),
    # GeoJSON/KML Individual View
    url(r'^(?P<geom_format>\w+)/(?P<geom_type>\w+)/(?P<feat_id>\d+)/$', 'geom_export'),
    # GeoJSON/KML Group Geometry URLs, note we're passing the additional 'group' dictionary value
    # to the view function.
    url(r'^(?P<geom_format>\w+)/(?P<geom_type>\w+)/group/(?P<feat_id>\d+)/$', 'geom_export', {'group':True}),
)