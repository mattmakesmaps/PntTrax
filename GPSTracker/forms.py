__author__ = 'matt'
from fiona import collection
from django import forms
from GPSTracker import file_uploads
from GPSTracker.models import Group
from django.core.exceptions import ValidationError
import zipfile
class shapefile_field(forms.FileField):
    """Accepts an archive containing a single shapefile."""

    def __init__(self, *args, **kwargs):
        super(shapefile_field, self).__init__(*args, **kwargs)
        self.shpName = None

    def validate(self, value):
        """A valid value will be an archive containing a single shapefile."""
        # Use the FileField valid method
        print 'In Validate'
        super(forms.FileField, self).validate(value)
        if value.content_type != 'application/zip':
            raise ValidationError(u'ERROR: Not a valid .zip file.')
        zippath = '/Users/matt/Projects/tmp/zips/'
        file_uploads.save_zip(zippath,value)
        self.shpName = file_uploads.decompress_zip(zippath,value.name)
        print self.shpName

def get_groups():
    """Return groups for a choice list"""
    group_list = Group.objects.all()
    group_choice = []
    for group in group_list:
        group_choice.append((group.id, group.name))
    return group_choice

def get_shpFields(shpPath):
    """Return a list of tuples denoting fields for a given shapefile.
    You need tuples for a choice field: https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.choices"""
    shpIn = collection(shpPath, "r")
    attributes = shpIn.schema['properties'].keys()
    attZip = zip(attributes,attributes)
    attZip.append((u'','None'))
    # use zip to create a list of tuples.
    # TODO: Need to add a None value or something for optional fields.
    return attZip

class UploadFileForm1(forms.Form):
    """
    Grab an uploaded file and all manual mappings provided by a user
    """
    def __init__(self, *args, **kwargs):
        super(UploadFileForm1, self).__init__(*args, **kwargs)
        self.fields['group'] = forms.ChoiceField(choices=get_groups())

    # https://docs.djangoproject.com/en/dev/ref/forms/api/#styling-required-or-erroneous-form-rows
    error_css_class = 'text-error'
    required_css_class = 'text-required'

    name = forms.CharField(label='Name')
    type = forms.CharField(label='Feature Type',required=False)
    method = forms.CharField(label='Collection Method', required=False)
    collectDate = forms.CharField(label='Collection Date', required=False)
    comment = forms.CharField(label='Comment',required=False)

    file = forms.FileField('File')

class betaUploadFileForm1(forms.Form):
    """
    First file upload form page. Take uploaded file from user and
    associate with a given GPS Group.
    """

    # https://docs.djangoproject.com/en/dev/ref/forms/api/#styling-required-or-erroneous-form-rows
    error_css_class = 'text-error'
    required_css_class = 'text-required'

    file = shapefile_field('File')

    def clean(self):
        cleaned_data = super(betaUploadFileForm1, self).clean()
        print cleaned_data
        return cleaned_data

class betaUploadFileForm2(forms.Form):
    """
    Grab an uploaded file and all manual mappings provided by a user
    """
    def __init__(self, *args, **kwargs):
        # http://stackoverflow.com/questions/987237/adding-a-kwarg-to-a-class
        self.shpPath = kwargs.pop('shpPath', None)
        super(betaUploadFileForm2, self).__init__(*args, **kwargs)
        self.attributeChoices = get_shpFields(self.shpPath)
        self.fields['group'] = forms.ChoiceField(choices=get_groups(), label='GPS Group')
        self.fields['name'] = forms.ChoiceField(choices=self.attributeChoices, label='Name')
        self.fields['type'] = forms.ChoiceField(choices=self.attributeChoices, required=False, label='Feature Type')
        self.fields['method'] = forms.ChoiceField(choices=self.attributeChoices, required=False, label='Collection Method')
        self.fields['collectDate'] = forms.ChoiceField(choices=self.attributeChoices, required=False, label='Collection Date')
        self.fields['comment'] = forms.ChoiceField(choices=self.attributeChoices, required=False, label='Comment')

    # https://docs.djangoproject.com/en/dev/ref/forms/api/#styling-required-or-erroneous-form-rows
    error_css_class = 'text-error'
    required_css_class = 'text-required'
