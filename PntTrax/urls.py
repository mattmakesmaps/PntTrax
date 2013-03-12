from django.conf.urls import patterns, include, url
from django.contrib.gis import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^gpstracker/', include('GPSTracker.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # Auth related URLs
    (r'^accounts/login', 'django.contrib.auth.views.login', {'template_name':'../templates/registration/login.html'}),
    (r'^accounts/logout', 'django.contrib.auth.views.logout'),
)
