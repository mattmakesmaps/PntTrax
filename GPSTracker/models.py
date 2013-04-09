import datetime
from django.contrib.gis.db import models
# Import Auth app's group mode. Alias to avoid conflicts with GPSTracker app.
# from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.models import AbstractUser

class Client(models.Model):
    """Information regarding the client"""
    name = models.CharField('Name', max_length=255, unique=True)
    city = models.CharField('City', max_length=255)
    state = models.CharField('State', max_length=255)

    # # http://stackoverflow.com/questions/12960258/django-check-diference-between-old-and-new-value-when-overriding-save-method
    # def save(self, *args, **kwargs):
    #     created = not self.pk
    #     if created: # New Value, INSERT as new value into Auth Group
    #         newGroup = AuthGroup(name=self.name)
    #         newGroup.save()
    #     else: # Old Value, UPDATE
    #         # To UPDATE, we need to get the original client name,
    #         # and the original existing related auth group.
    #         # Change the auth group to the new name.
    #         old_client = Client.objects.get(pk=self.pk)
    #         related_auth_group = AuthGroup.objects.get(name=old_client.name)
    #         related_auth_group.name = self.name
    #         related_auth_group.save()
    #
    #     super(Client, self).save(*args, **kwargs)
    #
    # # NOTE: this will not be called when using the bulk action.
    # def delete(self, using=None):
    #     related_auth_group = AuthGroup.objects.get(name=self.name)
    #     related_auth_group.delete()
    #     super(Client, self).delete()

    def __unicode__(self):
        return self.name

class GPSUser(AbstractUser):
    job_title = models.CharField('Job Title', max_length=255, blank=True)
    authorized_clients = models.ManyToManyField(Client)

class Group(models.Model):
    """A high-level container for related GPS locations."""
    name = models.CharField('Name',max_length=255,default='Unknown Group')
    client = models.ForeignKey(Client)
    pathway = models.CharField('File Pathway', max_length=500, blank=True)
    comment = models.CharField('Comment',max_length=255, blank=True)

    def __unicode__(self):
        return self.name

class FeaturePurpose(models.Model):
    """Different Purposes for GPS Feature. E.g. Photo Point, Sample Location."""
    purpose = models.CharField('Purpose', max_length=255,default='Unknown')

    def __unicode__(self):
        return self.purpose

def get_FeaturePurpose():
    """Used to set default FK value."""
    return FeaturePurpose.objects.get(purpose='Unknown')

class CollectionMethod(models.Model):
    """How was the feature collected? Trimble, Phone, Digitized?"""
    method = models.CharField('Collection Method', max_length=255,default='Unknown')

    def __unicode__(self):
        return self.method

def get_CollectionMethod():
    """Used to set default FK value."""
    return CollectionMethod.objects.get(method='Unknown')

class geomBase(models.Model):
    """Abstract base class for geometry tables."""
    name = models.CharField('Name',max_length=255, blank=True, default='Default Name')
    collectDate = models.DateField('Collection Date', blank=True, default=datetime.date(1901,1,1))
    collectTime = models.TimeField('Collection Time', blank=True, default=datetime.time(12,12,12))
    addDate = models.DateField('Add Date', auto_now_add=True)
    updateDate = models.DateField('Update Date', auto_now=True)
    comment = models.CharField('Comment',max_length=255, blank=True, default='')
    group = models.ForeignKey(Group)
    featurePurpose = models.ForeignKey(FeaturePurpose, default=get_FeaturePurpose)
    collectionMethod = models.ForeignKey(CollectionMethod, default=get_CollectionMethod)

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

class Point(geomBase):
    """Point Features"""
    lon = models.FloatField('Lon', blank=True, default=float(0))
    lat = models.FloatField('Lat', blank=True, default=float(0))

    geom = models.PointField('Point Geom')

class Line(geomBase):
    """Line Features"""
    geom = models.LineStringField('Line Geom')

class Poly(geomBase):
    """Polygon Features"""
    geom = models.PolygonField('Poly Geom')
