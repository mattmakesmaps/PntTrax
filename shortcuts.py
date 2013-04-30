import fiona, StringIO, tempfile, os, zipfile
from vectorformats.Formats import Django, GeoJSON, KML
from decimal import Decimal
from datetime import date, time
from json import dumps, loads

import django.db.models.base

def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise ImproperlyConfigured(error_msg)

# Utility Functions
def djangoToExportFormat(request, filter_object, properties_list=None, geom_col="geom", format="geojson"):
    """Convert a GeoDjango QuerySet to a GeoJSON Object"""

    #Workaround for mutable default value
    if properties_list is None:
        properties_list = []
        #Return dictionary of key value pairs
        filter_dict = filter_object[0].__dict__
        #Remove bunk fields
        for d in filter_dict:
            if isinstance(filter_dict[d], django.db.models.base.ModelState):
                pass
            # Convert decimal to float
            elif isinstance(filter_dict[d], Decimal):
                for obj in filter_object:
                    setattr(obj, d, float(obj.__dict__[d]))
                properties_list.append(d)
            # Convert date to string
            elif isinstance(filter_dict[d], date):
                for obj in filter_object:
                    setattr(obj, d, str(obj.__dict__[d]))
                properties_list.append(d)
            # Convert time to string
            elif isinstance(filter_dict[d], time):
                for obj in filter_object:
                    setattr(obj, d, str(obj.__dict__[d]))
                properties_list.append(d)
            else:
                properties_list.append(d)

        properties_list.remove(geom_col)

    queryset = filter_object
    djf = Django.Django(geodjango=geom_col, properties=properties_list)
    decode_djf = djf.decode(queryset)
    if format.lower() == 'geojson':
        geoj = GeoJSON.GeoJSON()
        # Pretty Print using JSON dumps method. Note requires setting
        # vectorformats encode method to_string param to False.
        s = dumps(geoj.encode(decode_djf, to_string=False), indent=4, separators=(',', ': '))
    elif format.lower() == 'kml':
        # title property can be passed as a keyword arg.
        # See vectorformats kml.py
        kml = KML.KML(title_property='name')
        s = kml.encode(decode_djf)
    elif format.lower() == 'shp':
        # convert to GeoJSON, then Use Fiona to Create a Shapefile.
        geoj = GeoJSON.GeoJSON()
        geoJSON = dumps(geoj.encode(decode_djf, to_string=False), indent=4, separators=(',', ': '))

        # Hard source properties for the destination shapefile.
        # These will be passed to Fiona.
        shp_driver = 'ESRI Shapefile'
        shp_crs = {'no_defs': True, 'ellps': 'WGS84', 'datum': 'WGS84', 'proj': 'longlat'}
        shp_schema = {'geometry': decode_djf[0].geometry['type'],
 'properties': {'addDate': 'str',
                'collectDate': 'str',
                'collectionMethod': 'str',
                'comment': 'str',
                'featurePurpose': 'str',
                'group': 'str',
                'name': 'str',
                'updateDate': 'str'}}

        try:
            upload_dir = tempfile.mkdtemp(dir=get_env_variable('UPLOAD_DIR'))
        except:
            upload_dir = tempfile.mkdtemp()

        zipdir = os.path.join(upload_dir, decode_djf[0].properties['group'])
        print zipdir

        with fiona.open(zipdir, 'w', driver=shp_driver, crs=shp_crs, schema=shp_schema) as dest_shp:
            for feature in decode_djf:
                out_feature = {'geometry': {}, 'properties': {}}
                for property in shp_schema['properties']:
                    out_feature['properties'][property] = feature['properties'][property]
                out_feature['geometry'] = feature['geometry']
                dest_shp.write(out_feature)

        # Create the zip archive
        zip = zipfile.ZipFile('%s.zip' % zipdir, 'w', zipfile.ZIP_DEFLATED)
        rootlen = len(zipdir) + 1
        for base, dirs, files in os.walk(zipdir):
           for file in files:
              fn = os.path.join(base, file)
              zip.write(fn, fn[rootlen:])

        s = zip.filename

    else:
        raise ValueError
    return s
