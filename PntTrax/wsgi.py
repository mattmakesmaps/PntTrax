"""
WSGI config for PntTrax project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os, sys

# Map OS Environment variables to those set in httpd.conf

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
_application = get_wsgi_application()

def application(environ, start_response):
    os.environ['PYTHONPATH'] = environ['PYTHONPATH']
    os.environ['SECRET_KEY'] = environ['PYTHONPATH']
    os.environ['DB_NAME'] = environ['DB_NAME']
    os.environ['DB_USER'] = environ['DB_USER']
    os.environ['DB_PASSWORD'] = environ['DB_PASSWORD']
    os.environ['DB_ENGINE'] = environ['DB_ENGINE']
    os.environ['UPLOAD_DIR'] = environ['UPLOAD_DIR']
    os.environ['DJANGO_SETTINGS_MODULE'] = environ['DJANGO_SETTINGS_MODULE']
    os.environ['EMAIL_HOST'] = environ['EMAIL_HOST']
    os.environ['EMAIL_HOST_USER'] = environ['EMAIL_HOST_USER']
    os.environ['EMAIL_HOST_PASSWORD'] = environ['EMAIL_HOST_PASSWORD']
    os.environ['EMAIL_PORT'] = environ['EMAIL_PORT']
    os.environ['EMAIL_USE_TLS'] = environ['EMAIL_USE_TLS']
    return _application(environ, start_response)

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
