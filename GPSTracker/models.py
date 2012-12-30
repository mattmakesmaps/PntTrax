from django.contrib.gis.db import models

class Client(models.Model):
    """Information regarding the client"""
    name = models.CharField('Name', max_length=255)
    city = models.CharField('City', max_length=255)
    state = models.CharField('State', max_length=255)

    geom = models.PolygonField('Client Boundary', blank=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

class Report(models.Model):
    """Reports for a client, in which GPS points were used."""
    name = models.CharField('Report Name', max_length=255)
    client = models.ForeignKey(Client)
    date = models.DateField('Report Date', blank=True)
    comment = models.CharField('Comment', max_length=255, blank=True)

    def __unicode__(self):
        return self.name

class Group(models.Model):
    """A high-level container for related GPS locations."""
    name = models.CharField('Name',max_length=255,blank=True)
    client = models.ForeignKey(Client)
    report = models.ManyToManyField(Report)
    pathway = models.CharField('File Pathway', max_length=500, blank=True)
    comment = models.CharField('Comment',max_length=255, blank=True)

    def __unicode__(self):
        return self.name

class Point(models.Model):
    """The Actual GPS Point."""
    typeChoices = (
        ('pp','Photo Point'),
        ('samp','Sample Location'),
        ('sitefeat','Site Feature'),
        ('other','Other'),
    )

    collectionChoices = (
        ('digit','Digitized'),
        ('gps','GPS')
    )
    name = models.CharField('Name',max_length=255, default='')
    type = models.CharField('Type', choices=typeChoices, max_length=255, blank=True, default='')
    method = models.CharField('Collection Method', choices=collectionChoices, max_length=255, blank=True, default='samp')
    collectDate = models.DateTimeField('Collection Date', blank=True, default='')
    addDate = models.DateTimeField('Collection Date', default='1901-01-01', auto_now_add=True)
    updateDate = models.DateTimeField('Collection Date', auto_now=True)
    comment = models.CharField('Comment',max_length=255, blank=True, default='')
    group = models.ForeignKey(Group, blank=True, default='')
    lon = models.FloatField('Lon', blank=True, default='')
    lat = models.FloatField('Lat', blank=True, default='')

    geom = models.PointField('Point Geom')
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

class Line(models.Model):
    """The Actual GPS Point."""
    typeChoices = (
        ('tran','Transect'),
        ('samp','Sample Location'),
        ('sitefeat','Site Feature'),
        ('other','Other'),
    )

    collectionChoices = (
        ('digit','Digitized'),
        ('gps','GPS')
    )
    name = models.CharField('Name',max_length=255)
    type = models.CharField('Type', choices=typeChoices, max_length=255, blank=True)
    method = models.CharField('Collection Method', choices=collectionChoices, max_length=255, blank=True)
    collectDate = models.DateTimeField('Collection Date', blank=True)
    addDate = models.DateTimeField('Collection Date', auto_now_add=True)
    updateDate = models.DateTimeField('Collection Date', auto_now=True)
    comment = models.CharField('Comment',max_length=255, blank=True)
    group = models.ForeignKey(Group)

    geom = models.LineStringField('Line Geom')
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

class Poly(models.Model):
    """The Actual GPS Point."""
    typeChoices = (
        ('sb','Site Boundary'),
        ('sitefeat','Site Feature'),
        ('other','Other'),
    )
    collectionChoices = (
        ('digit','Digitized'),
        ('gps','GPS')
    )
    name = models.CharField('Name',max_length=255)
    type = models.CharField('Type', choices=typeChoices, max_length=255, blank=True)
    method = models.CharField('Collection Method', choices=collectionChoices, max_length=255, blank=True)
    collectDate = models.DateTimeField('Collection Date', blank=True)
    addDate = models.DateTimeField('Collection Date', auto_now_add=True)
    updateDate = models.DateTimeField('Collection Date', auto_now=True)
    comment = models.CharField('Comment',max_length=255, blank=True)
    group = models.ForeignKey(Group)

    geom = models.PolygonField('Poly Geom')
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name