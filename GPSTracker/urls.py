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
    # Point GeoJSON View
    url(r'^geojson/point/(?P<feat_id>\d+)/$', 'geojson'),
    # Line GeoJSON View
    url(r'^geojson/line/(?P<feat_id>\d+)/$', 'geojson'),
    # Poly GeoJSON View
    url(r'^geojson/poly/(?P<feat_id>\d+)/$', 'geojson'),
    # GeoJSON/KML Group Geometry URLs
    url(r'^(?P<geom_format>\w+)/(?P<geom_type>\w+)/group/(?P<feat_id>\d+)/$', 'geom_group'),
)