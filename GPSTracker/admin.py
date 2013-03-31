from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.gis import admin
from django.contrib.auth.admin import UserAdmin
from models import *

class ClientAdmin(admin.GeoModelAdmin):
    list_display = ('name','city','state')
    list_editable = ('city','state')
    list_filter = ('state',)
    pass
admin.site.register(Client, ClientAdmin)

class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = GPSUser

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class GPSUserAdmin(UserAdmin):
    # Associate the change form
    form = UserChangeForm

    # Override the default fields
    fieldsets = (
        (None, {'fields':('password','last_login','date_joined')}),
        ('Personal Information', {'fields':('first_name','last_name','email','job_title')}),
        ('Authentication', {'fields':('is_staff','is_active','is_superuser','groups',
                                      'user_permissions','authorized_clients')})
    )
admin.site.register(GPSUser, GPSUserAdmin)

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
