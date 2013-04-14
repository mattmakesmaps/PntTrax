__author__ = 'matt'
import zipfile, os, datetime, logging, tempfile, shutil
from datetime import date
from fiona import collection
from django.core.exceptions import ValidationError
from django.core.exceptions import ImproperlyConfigured
from django.contrib.gis import geos
from django.db.models.fields import DateField, TimeField
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

    def get_seperator(self, inStr):
        """
        Given a string, return the seperator.
        Useful for implementation of date/time.
        Implements a search pattern
        """
        seperators = ['/','-','.']
        for val in seperators:
            if val in inStr:
                return val
        else:
            return None

    def string_to_date(self, inStr):
        """
        Given a string in the format of YYYY/MM/DD,
        Return a Python Date object.

        See get_seperator() for list of applicable
        delimiter values.
        """
        dateSplit = map(int,inStr.split(self.get_seperator(inStr)))
        return date(dateSplit[0], dateSplit[1], dateSplit[2])

    def string_to_time(self, inStr):
        """
        Given a string representation of a time, convert that to
        a Python time object.

        Examples of applicable times are:
        - '09:30:22PM'
        - '09:30PM
        - '21:30:22'
        - '21:30'
        """

        # check to see if AM/PM is in string. if not, consider a 24-hr clock.
        if inStr[len(timeVal)-2:] in ['am','pm']:
            hour = '%I'
            time_type = '%p'
        else:
            hour = '%H'
            time_type = ''

        # Inspect to see if there are three integers seperated by colons.
        if len(inStr.split(':')) == 2:
            # Time is formatted HH:MM
            format = hour + ':%M' + time_type
        elif len(inStr.split(':')) == 3:
            # HH:MM:SS
            format = hour + ':%M:%S' + time_type
        else:
            # Can't determine formatting. Bail.
            break
        return datetime.datetime.strptime(inStr.upper(), format).time()

    def import_shapefile(self, cleaned_data):
        """
        Draft script to import shapefile.
        """
        logger.info('Server Pathway: %s' % self.upload_full_path)
        logger.info('User-Provided Field Mapping: %s' % cleaned_data)

        # Create a fiona collection and process individual records
        with collection(self.upload_full_path, 'r') as inShp:
            # A mapping for keys representing geometry types (parsed from fiona)
            # To values representing destination model objects, and GEOS geometry
            # objects, used for import into GeoDjango
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
                # Dict with keys representing GeoDjango model field names, and values representing
                # data for a given feature (grabbed from fiona).
                modelMap = {}
                # iterate through a list of destinaionModel's field names.
                for model_field, model_field_type in [(x.name, type(x)) for x in destinationModel._meta.fields]:
                    for key in cleaned_data.iterkeys():
                        if model_field == key:
                            try:
                                # Handle Conversion of DateField and TimeFields
                                if model_field_type == DateField  and type(feat['properties'][cleaned_data[model_field]]) in [unicode, str]:
                                    modelMap[model_field] = self.string_to_date(feat['properties'][cleaned_data[model_field]])
                                elif model_field_type == TimeField:
                                    modelMap[model_field] = self.string_to_time(feat['properties'][cleaned_data[model_field]])
                                else:
                                    # If a NULL value is encountered, set to an empty string
                                    if feat['properties'][cleaned_data[model_field]]:
                                        modelMap[model_field] = feat['properties'][cleaned_data[model_field]]
                                    else:
                                        modelMap[model_field] = ''
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
