from django.contrib.gis.db import models
import datetime

class Client(models.Model):
    """Information regarding the client"""
    name = models.CharField('Name', max_length=255)
    city = models.CharField('City', max_length=255)
    state = models.CharField('State', max_length=255)

    def __unicode__(self):
        return self.name

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

class CollectionMethod(models.Model):
    """How was the feature collected? Trimble, Phone, Digitized?"""
    method = models.CharField('Collection Method', max_length=255,default='Unknown')

    def __unicode__(self):
        return self.method

class Point(models.Model):
    """The Actual GPS Point."""
    name = models.CharField('Name',max_length=255, default='Default Name')
    collectDate = models.DateField('Collection Date', blank=True, default=datetime.date(1901,1,1))
    collectTime = models.TimeField('Collection Time', blank=True, default=datetime.time(12,12,12))
    addDate = models.DateField('Add Date', auto_now_add=True)
    updateDate = models.DateField('Update Date', auto_now=True)
    comment = models.CharField('Comment',max_length=255, blank=True, default='')
    group = models.ForeignKey(Group)
    featurePurpose = models.ForeignKey(FeaturePurpose)
    collectionMethod = models.ForeignKey(CollectionMethod)
    lon = models.FloatField('Lon', blank=True, default=float(0))
    lat = models.FloatField('Lat', blank=True, default=float(0))

    geom = models.PointField('Point Geom')
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

class Line(models.Model):
    """The Actual GPS Point."""
    name = models.CharField('Name',max_length=255, default='Default Name')
    collectDate = models.DateField('Collection Date', blank=True, default=datetime.date(1901,1,1))
    collectTime = models.TimeField('Collection Time', blank=True, default=datetime.time(12,12,12))
    addDate = models.DateField('Add Date', auto_now_add=True)
    updateDate = models.DateField('Update Date', auto_now=True)
    comment = models.CharField('Comment',max_length=255, blank=True, default='')
    group = models.ForeignKey(Group)
    featurePurpose = models.ForeignKey(FeaturePurpose)
    collectionMethod = models.ForeignKey(CollectionMethod)

    geom = models.LineStringField('Line Geom')
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

class Poly(models.Model):
    """The Actual GPS Point."""
    name = models.CharField('Name',max_length=255, default='Default Name')
    collectDate = models.DateField('Collection Date', blank=True, default=datetime.date(1901,1,1))
    collectTime = models.TimeField('Collection Time', blank=True, default=datetime.time(12,12,12))
    addDate = models.DateField('Add Date', auto_now_add=True)
    updateDate = models.DateField('Update Date', auto_now=True)
    comment = models.CharField('Comment',max_length=255, blank=True, default='')
    group = models.ForeignKey(Group)
    featurePurpose = models.ForeignKey(FeaturePurpose)
    collectionMethod = models.ForeignKey(CollectionMethod)

    geom = models.PolygonField('Poly Geom')
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name