from django.contrib.gis import admin
from models import *

class ClientAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(Client, ClientAdmin)

class GroupAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(Group, GroupAdmin)

class FeaturePurposeAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(FeaturePurpose, FeaturePurposeAdmin)

class CollectionMethodAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(CollectionMethod, CollectionMethodAdmin)

class PointAdmin(admin.OSMGeoAdmin):
    list_display = ['name','collectDate','group','featurePurpose','collectionMethod']
    list_editable = ['featurePurpose','collectionMethod']
admin.site.register(Point, PointAdmin)

class LineAdmin(admin.OSMGeoAdmin):
    list_display = ['name','collectDate','group','featurePurpose','collectionMethod']
    list_editable = ['featurePurpose','collectionMethod']
admin.site.register(Line, LineAdmin)

class PolyAdmin(admin.OSMGeoAdmin):
    list_display = ['name','collectDate','group','featurePurpose','collectionMethod']
    list_editable = ['featurePurpose','collectionMethod']
admin.site.register(Poly, PolyAdmin)
