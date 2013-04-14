__author__ = 'matt'
import zipfile, os, datetime, logging, tempfile, shutil
from datetime import date
from fiona import collection
from django.core.exceptions import ValidationError
from django.core.exceptions import ImproperlyConfigured
from django.contrib.gis import geos
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
        self.upload_dir = None
        self.in_memory_file = in_memory_file
        self.shp_name = None
        self.upload_full_path = None
        self.decompress_zip()


    def decompress_zip(self):
        """
        Decompress zip file into a temporary directory.
        Return a string rep of the .shp filename
        """
        zfile = zipfile.ZipFile(self.in_memory_file)

        # Check if UPLOAD_DIR environment variable is set.
        # If not, allow tempfile to determine folder location.
        try:
            zfile_dir = tempfile.mkdtemp(dir=get_env_variable('UPLOAD_DIR'))
        except:
            zfile_dir = tempfile.mkdtemp()

        for name in zfile.namelist():
            fd = open(os.path.join(zfile_dir, name),"wb+")
            fd.write(zfile.read(name))
            fd.close()
            # Return the shapefile file name.
            if name[len(name)-3:] == 'shp':
                shpName = name
                self.shp_name = shpName

        self.upload_dir = zfile_dir
        self.upload_full_path = os.path.join(zfile_dir, shpName)
        return self.upload_full_path

    def remove_directory(self, inDir):
        """
        Given a directory, remove it an its contents.
        Intended to clean up temporary files after upload.
        """
        shutil.rmtree(inDir)
        logger.info('Delete Successful: %s' % inDir)


    def import_shapefile(self, cleaned_data):
        """
        Draft script to import shapefile.
        """
        logger.info('Server Pathway: %s' % self.upload_full_path)
        logger.info('User-Provided Field Mapping: %s' % cleaned_data)

        # Create a fiona collection and process individual records
        with collection(self.upload_full_path, 'r') as inShp:

            gps_tracker_model_map = {'Point':(Point, geos.Point),
                                    'LineString':(Line, geos.LineString),
                                    'Polygon':(Poly, geos.Polygon)}

            if inShp.schema['geometry'] in gps_tracker_model_map:
                destinationModel, destinationGeos = gps_tracker_model_map[inShp.schema['geometry']]

            for feat in inShp:
                # Pass In GEOS Geoms, format is specific to geometry type.
                if inShp.schema['geometry'] == 'Point':
                    GEOSGeomObject = destinationGeos(feat['geometry']['coordinates'])
                elif inShp.schema['geometry'] == 'LineString':
                    GEOSGeomObject = destinationGeos(tuple(feat['geometry']['coordinates']))
                # Construct LinearRings from Fiona Coordinates, and pass to GEOS polygon constructor.
                elif inShp.schema['geometry'] == 'Polygon':
                    rings = []
                    for ring in feat['geometry']['coordinates']:
                        rings.append(geos.LinearRing(ring))
                    GEOSGeomObject = destinationGeos(*rings)
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

        # Remove the tempfile directory.
        self.remove_directory(self.upload_dir)
        return True
