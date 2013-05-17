__author__ = 'matt'
import zipfile, os, datetime, logging, tempfile, shutil, json
from dateutil.parser import parse
from fiona import collection
from django.core.exceptions import ImproperlyConfigured
from django.contrib.gis import geos
from django.db.models.fields import DateField, TimeField
from .models import Point, Line, Poly, Group
from shortcuts import remove_temp_dir, make_temp_dir, get_env_variable

logger = logging.getLogger(__name__)

class ShpUploader(object):
    """
    # A class containing all methods associated with
    # Uploading a shapefile into PntTrax

    # CLASS NOTE: Check out the third-party pyshapelib package.
    """

    def __init__(self, in_memory_file):
        """
        decompress_zip() sets all attribute values
        except for in_memory_file.
        """
        self.in_memory_file = in_memory_file
        self.upload_dir = make_temp_dir()
        # Execute Decompress Zip
        self.decompress_zip()

    def decompress_zip(self):
        """
        Decompress zip file into a temporary directory.
        Return a string rep of the .shp filename
        """
        zfile = zipfile.ZipFile(self.in_memory_file)

        for name in zfile.namelist():
            fd = open(os.path.join(self.upload_dir, name),"wb+")
            fd.write(zfile.read(name))
            fd.close()
            # Return the shapefile file name.
            if name[len(name)-3:] == 'shp':
                self.shp_name = name

        self.upload_full_path = os.path.join(self.upload_dir, self.shp_name)
        return self.upload_full_path

    def import_shapefile(self, cleaned_data):
        """
        Given a dictionary, 'cleaned_data', of keys representing django model fields
        (point, line, poly), and values representing their user-defined mappings
        to an uploaded shapefile's fields, import a shapefile's data into the GPSTracker
        database.

        The process is roughly as follows:
        1. Using fiona, open a user uploaded shapefile (SHP).
        2. Determine the appropriate Django Model (Point, LineString, Polygon).
        3. Loop through each feature in the SHP
        3a. For each feature, build a dictionary, 'destinationData', containing keys
            representing django model field names, and values representing SHP attribute
            values.
        3b. Create an instance of the Django Model, passing in 'destinationData'
            to the constructor.
        3c. Call the instance's save method to import the feature.
        4. After all features are inserted, close the SHP,
           delete the SHP and it's temp directory.
        """
        logger.info('Server Pathway: %s' % self.upload_full_path)
        logger.info('User-Provided Field Mapping: %s' % cleaned_data)

        # Create a fiona collection and process individual records
        with collection(self.upload_full_path, 'r') as inShp:
            # keys representing geometry types (parsed from fiona) to Django Models
            gps_tracker_model_map = {'Point':Point,
                                    'LineString':Line,
                                    'Polygon':Poly}
            if inShp.schema['geometry'] in gps_tracker_model_map:
                destinationModel = gps_tracker_model_map[inShp.schema['geometry']]

            for feat in inShp:
                """
                # DEPRECATED CLASS NOTE:
                # The if/elif/else code emulates a switch.
                # You could create a function for each case,
                # and use a dict lookup (as in gps_tracker_model_map)
                # But you could also just create subclasses that insert
                # geometry specific fucntionality.
                """
                """
                # Given a string representation of the Fiona GeoJSON-like geom representation,
                # Replace parens with brackets for GeoJSON-input parsing by GEOS.
                """
                GEOSGeomObject = geos.GEOSGeometry(json.dumps(feat['geometry']))
                # Dict with keys representing GeoDjango model field names, and values representing
                # data for a given feature (grabbed from fiona).
                destinationData = {}
                modelFieldAttrs = {x.name: type(x) for x in destinationModel._meta.fields}
                for key in cleaned_data.iterkeys():
                    try:
                        # Check to see if real values exist first
                        if feat['properties'][cleaned_data[key]]:
                        # Handle Conversion of DateField and TimeFields
                            if modelFieldAttrs[key] == DateField  and type(feat['properties'][cleaned_data[key]]) in [unicode, str]:
                                destinationData[key] = parse(feat['properties'][cleaned_data[key]])
                            elif modelFieldAttrs[key] == TimeField:
                                destinationData[key] = parse(feat['properties'][cleaned_data[key]]).time()
                            else:
                                destinationData[key] = feat['properties'][cleaned_data[key]]
                        # else:
                        #     pass
                    except KeyError:
                        """
                        KeyError is raised when the loop attempts to process 'group' value.
                        In 'cleaned_data', 'group' key is associated to the FK ID of the actual
                        GPS group, as opposed to a field name. When we try and grab the attribute
                        value in the source SHP using feat['properties'][cleaned_data[key]], we are
                        actually passing in the FK ID (e.g. 1, 2, 3) as a key to feat['properties'].

                        Value for group is populated correctly outside of the loop.

                        TODO: Better way to handle this exception.
                        """
                        pass

                # Add Group and Geom to modelMap
                destinationData['group'] = Group.objects.get(pk=cleaned_data['group'])
                destinationData['geom'] = GEOSGeomObject

                # Pass dictionary as kwargs and save
                outFeat = destinationModel(**destinationData)
                outFeat.save()
            # Delete Temporary Directory
            if remove_temp_dir(self.upload_dir):
                logger.info("Delete Successful: %s" % self.upload_dir)

        return True
