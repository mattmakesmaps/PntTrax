__author__ = 'matt'
from django.conf.urls import patterns, url

urlpatterns = patterns('GPSTracker.views',
    # Index
    url(r'^$', 'index'),
    # Root of the client based views
    url(r'^clients/$', 'clients'),
    # About
    url(r'^about/$', 'about'),
    # Group View
    url(r'^groups/(?P<client_id>\d+)/$', 'group'),
    # Group Detail View
    url(r'^groups/detail/(?P<group_id>\d+)/$', 'group_detail'),
    # GeoJSON/KML Individual View
    url(r'^(?P<geom_format>\w+)/(?P<geom_type>\w+)/(?P<feat_id>\d+)/$', 'geom_export'),
    # GeoJSON/KML Group Geometry URLs, note we're passing the additional 'group' dictionary value
    # to the view function.
    url(r'^(?P<geom_format>\w+)/(?P<geom_type>\w+)/group/(?P<feat_id>\d+)/$', 'geom_export', {'group':True}),
    ## UPLOAD FILES
    url(r'^uploadfile/$', 'uploadfile1'),
    url(r'^uploadfile/2$', 'uploadfile2'),
    url(r'^uploadfile/success/$', 'upload_success'),
)
