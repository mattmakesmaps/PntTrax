__author__ = 'matt'
from fiona import collection
from django.contrib.gis.gdal import DataSource
from GPSTracker.models import Point, Line, Poly, Group
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
    # Change zip name to shp extension for processing.
    # This assumes that the zip is named the same as
    # the shapefile
    shpName = cleaned_data['file'].name[:-4] + '.shp'
    if zip: decompress_zip(zippath, cleaned_data['file'].name)

    ds = DataSource(os.path.join(zippath, shpName))
    layer = ds[0]

    # Select appropriate Django Destination Model
    ogcGeom = {'Point':Point,'LineString':Line,'Polygon':Poly}
    if layer.geom_type.name in ogcGeom:
        destinationModel = ogcGeom[layer.geom_type.name]

    # LayerMapping
    mapping = {
        'collectDate':cleaned_data['collectDate_field'],
        'comment':cleaned_data['comment_field'],
        # Getting error that group field is not in OGR Layer.
        # Think I'll add the group key after save.
        'group':cleaned_data['gps_group'],
#        'method':cleaned_data['method_field'],
        'name':cleaned_data['name_field'],
#        'type':cleaned_data['type_field'],
#        'geom':layer.geom_type.name,
    }

    # Only pass on those fields which have been properly mapped
    populatedMapping = {}
    for key, value in mapping.iteritems():
        if len(value) >= 1:
            populatedMapping[key] = value

     # Create a fiona collection and process individual records
    with collection(os.path.join(zippath, shpName), 'r') as inShp:
        for feat in inShp:
            # Add a foreign key back to group for each record before save
            feat['properties']['group']=Group.objects.get(pk=cleaned_data['gps_group'])

            for field, value in feat['properties'].iteritems():
                if field in populatedMapping.itervalues():
                    print "field: %s" % field
                    print "value: %s" % value

#    lm = LayerMapping(destinationModel, os.path.join(zippath, shpName), populatedMapping)
#    lm.save(verbose=True)


    return True
