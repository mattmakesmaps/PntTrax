from django.conf.urls import patterns, include, url
from django.contrib.gis import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^gpstracker/', include('GPSTracker.urls', namespace='GPSTracker')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Auth related URLs
    url(r'^accounts/login', 'django.contrib.auth.views.login', {'template_name':'../templates/registration/login.html'}),
    url(r'^accounts/logout', 'django.contrib.auth.views.logout'),
)
