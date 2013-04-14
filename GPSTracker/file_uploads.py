__author__ = 'matt'
import logging
import zipfile, os, datetime
from datetime import date
from fiona import collection
from django.core.exceptions import ValidationError
from django.core.exceptions import ImproperlyConfigured
from django.contrib.gis import geos
from django.contrib.gis.gdal import DataSource
from .models import Point, Line, Poly, Group

logger = logging.getLogger(__name__)

def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise ImproperlyConfigured(error_msg)

class ShpUploader(object):
    """
    # A class containing all methods associated with
    # Uploading a shapefile into PntTrax
    """

    def __init__(self, in_memory_file):
        self.upload_dir = get_env_variable('UPLOAD_DIR')
        self.in_memory_file = in_memory_file
        self.shp_name = None
        self.decompress_zip()

    @property
    def upload_full_path(self):
        return os.path.join(self.upload_dir, self.shp_name)

    def decompress_zip(self):
        """
        Decompress all files in a zip archive.
        Return a string rep of the .shp filename.
        """
        # http://stackoverflow.com/a/7806727
        # zipfullpath = os.path.join(self.upload_dir, file)
        zfile = zipfile.ZipFile(self.in_memory_file)
        for name in zfile.namelist():
            fd = open(os.path.join(self.upload_dir, name),"wb+")
            fd.write(zfile.read(name))
            fd.close()
            # Return the shapefile file name.
            if name[len(name)-3:] == 'shp':
                shpName = name
                self.shp_name = shpName
        return os.path.join(self.upload_dir, shpName)

    def import_shapefile(self, cleaned_data, shpPath):
        """
        Draft script to import shapefile.
        """
        ds = DataSource(shpPath)
        layer = ds[0]

        logger.info('Server Pathway: %s' % ds)
        logger.info('User-Provided Field Mapping: %s' % cleaned_data)

        # Select appropriate Django Destination Model
        ogcGeom = {'Point':Point,'LineString':Line,'Polygon':Poly}
        if layer.geom_type.name in ogcGeom:
            destinationModel = ogcGeom[layer.geom_type.name]

            # Create a fiona collection and process individual records
        with collection(shpPath, 'r') as inShp:
            for feat in inShp:
                # Create GEOSGeometry Object
                GEOSGeomDict = {'Point':geos.Point,'LineString':geos.LineString,'Polygon':geos.Polygon}

                if layer.geom_type.name == 'Point':
                    GEOSGeomObject = GEOSGeomDict[layer.geom_type.name](feat['geometry']['coordinates'])
                elif layer.geom_type.name == 'LineString':
                    GEOSGeomObject = GEOSGeomDict[layer.geom_type.name](tuple(feat['geometry']['coordinates']))
                # Construct LinearRings from Fiona Coordinates, and pass to GEOS polygon constructor.
                elif layer.geom_type.name == 'Polygon':
                    rings = []
                    for ring in feat['geometry']['coordinates']:
                        rings.append(geos.LinearRing(ring))
                    print rings
                    GEOSGeomObject = GEOSGeomDict[layer.geom_type.name](*rings)
                    # List representing model fields we're interested in.
                # TODO: Introspect a model's fields and generate list dynamically.
                dataFields = ['collectDate','collectTime','comment','name','type','method']
                # Dict with keys representing GeoDjango model field names, and values representing
                # data for a given feature (grabbed from fiona).
                modelMap = {}
                for field in dataFields:
                    for key in cleaned_data.iterkeys():
                        if field == key:
                            try:
                                # Check if date field is string or python date type
                                if field == 'collectDate' and type(feat['properties'][cleaned_data[field]]) == unicode:
                                    dateStr = feat['properties'][cleaned_data[field]]
                                    # Assumes a date separator of '/'. convert to int for datetime.date
                                    dateSplit = map(int,dateStr.split('/'))
                                    dateObject = date(dateSplit[0], dateSplit[1], dateSplit[2])
                                    modelMap[field] = dateObject
                                elif field == 'collectTime':
                                    timeVal = feat['properties'][cleaned_data[field]]

                                    # check to see if AM/PM is in string. if not, consider a 24-hr clock.
                                    if timeVal[len(timeVal)-2:] in ['am','pm']:
                                        hour = '%I'
                                        time_type = '%p'
                                    else:
                                        hour = '%H'
                                        time_type = ''

                                    # Inspect to see if there are three integers seperated by colons.
                                    if len(timeVal.split(':')) == 2:
                                        # Time is formatted HH:MM
                                        format = hour + ':%M' + time_type
                                    elif len(timeVal.split(':')) == 3:
                                        # HH:MM:SS
                                        format = hour + ':%M:%S' + time_type
                                    else:
                                        # Can't determine formatting. Bail.
                                        break
                                    modelMap[field] = datetime.datetime.strptime(timeVal.upper(), format).time()

                                else:
                                    # If a NULL value is encountered, set to an empty string
                                    if feat['properties'][cleaned_data[field]]:
                                        modelMap[field] = feat['properties'][cleaned_data[field]]
                                    else:
                                        modelMap[field] = ''
                            except KeyError:
                                pass
                    # Add Group and Geom to modelMap
                modelMap['group'] = Group.objects.get(pk=cleaned_data['group'])
                modelMap['geom'] = GEOSGeomObject

                # Pass dictionary as kwargs and save
                outFeat = destinationModel(**modelMap)
                outFeat.save()
        return True
