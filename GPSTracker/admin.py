from django.contrib.gis import admin
from models import *

class ClientAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(Client, ClientAdmin)

class ReportAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(Report, ReportAdmin)

class GroupAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(Group, GroupAdmin)

class PointAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(Point, PointAdmin)

class LineAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(Line, LineAdmin)

class PolyAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(Poly, PolyAdmin)
