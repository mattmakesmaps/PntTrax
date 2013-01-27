from django.contrib.gis import admin
from models import *

class ClientAdmin(admin.GeoModelAdmin):
    list_display = ('name','city','state')
    list_editable = ('city','state')
    list_filter = ('state',)
    pass
admin.site.register(Client, ClientAdmin)

class GroupAdmin(admin.GeoModelAdmin):
    list_display = ('name','client','pathway','comment')
    list_editable = ('client','pathway','comment')
    pass
admin.site.register(Group, GroupAdmin)

class FeaturePurposeAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(FeaturePurpose, FeaturePurposeAdmin)

class CollectionMethodAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(CollectionMethod, CollectionMethodAdmin)

# Geometry Table Admins
class PntTraxGeoAdmin(admin.OSMGeoAdmin):
    """Base Class for Geometry Table Admin"""
    list_display = ('name','collectDate','group','featurePurpose','collectionMethod')
    list_editable = ('featurePurpose','group','collectionMethod')
    list_filter = ('featurePurpose','group__name')

class PointAdmin(PntTraxGeoAdmin):
    """Point Admin"""
    pass
admin.site.register(Point, PointAdmin)

class LineAdmin(PntTraxGeoAdmin):
    """Line Admin"""
    pass
admin.site.register(Line, LineAdmin)

class PolyAdmin(PntTraxGeoAdmin):
    """Poly Admin"""
    pass
admin.site.register(Poly, PolyAdmin)
