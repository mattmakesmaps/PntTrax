__author__ = 'matt'
from django.contrib.gis import geos
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
        destinationModel = ogcGeom[layer.geom_type.name]()

     # Create a fiona collection and process individual records
    with collection(os.path.join(zippath, shpName), 'r') as inShp:

        for feat in inShp:
            # Create GEOSGeometry Object
            GEOSGeomDict = {'Point':geos.Point,'LineString':geos.LineString,'Polygon':geos.Polygon}
            # This will only work for points
            # See http://toblerity.github.com/fiona/manual.html#record-geometry
            if layer.geom_type.name in ogcGeom:
                GEOSGeomObject = GEOSGeomDict[layer.geom_type.name](feat['geometry']['coordinates'])

            # LayerMapping
            ModelValueMap = {
                'collectDate':feat['properties'][cleaned_data['collectDate_field']],
                'comment':feat['properties'][cleaned_data['comment_field']],
                'group':Group.objects.get(pk=cleaned_data['gps_group']),
                #        'method':cleaned_data['method_field'],
                'name':feat['properties'][cleaned_data['name_field']],
                #        'type':cleaned_data['type_field'],
                'geom':GEOSGeomObject,
            }

            # Only pass on those fields which have been properly mapped
            populatedModelValueMap = {}
            for key, value in ModelValueMap.iteritems():
                if value <> u'':
                    populatedModelValueMap[key] = value

            # Try and Save To Model
            destinationModel.save(populatedModelValueMap)

            # TEST: WILL CALL SAVE METHOD USING populatedModelValueMap
            for key, value in populatedModelValueMap.iteritems():
                print key, value

    return True
