__author__ = 'matt'
from django.contrib.gis.gdal import DataSource
from GPSTracker.models import Point, Line, Poly
import zipfile, os

def save_zip(path, f):
    """Save an uploaded file to tmp"""
    """
    TODO: Will fail if directory doesn't exist. Won't fail if file doesn't exist.
    """
    try:
        with open(path + f.name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
        return True
    except Exception:
        raise Exception


def decompress_zip(path, file):
    """Decompress all files in a zip archive."""
    # http://stackoverflow.com/a/7806727
    zipfullpath = os.path.join(path, file)
    zfile = zipfile.ZipFile(zipfullpath)
    for name in zfile.namelist():
        print name
        fd = open(os.path.join(path,name),"wb+")
        fd.write(zfile.read(name))
        fd.close()

def import_shapefile(cleaned_data):
    """
    Draft script to process an uploaded shapefile.
    """
    # If uploaded file is a zip, save it.
    zippath = '/Users/matt/Projects/tmp/zips/'
    zip = save_zip(zippath,cleaned_data['file'])
    if zip: decompress_zip(zippath, cleaned_data['file'].name)

    return True
