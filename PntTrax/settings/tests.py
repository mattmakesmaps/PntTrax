__author__ = 'matt'
"""Local test settings and globals which allows us to run our
test suite locally."""
from base import *
########## TEST SETTINGS
TEST_DISCOVER_TOP_LEVEL = DJANGO_ROOT
TEST_DISCOVER_ROOT = DJANGO_ROOT
TEST_DISCOVER_PATTERN = "*"
########## IN-MEMORY TEST DATABASE
DATABASES = {
    "default": {
        "ENGINE":"django.contrib.gis.db.backends.spatialite",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
        }, }
