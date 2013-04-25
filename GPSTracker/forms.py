__author__ = 'matt'
from fiona import collection
from django import forms
from django.core.exceptions import ValidationError
from .models import Group
import zipfile

def validate_shp(value):
    """
    Raises validation errors for an uploaded file in the following cases:
    * not a zip.
    * zip, but no shp.
    * zip, but multiple shp.
    * no PRJ file.
    * non-WGS84 PRJ File.

    Parses in-memory zipfile for filenames.
    """

    """Raise ValidationError if input is not a zip file."""
    if value.name[len(value.name)-3:].lower() <> 'zip':
        raise ValidationError(u'File Error: Not a valid .zip file.')

    filenames = zipfile.ZipFile(value).namelist()
    # Create a list of files ending in 'shp'
    shpFiles = [file for file in filenames if file[len(file)-3:] == 'shp']
    if len(shpFiles) == 0:
        raise ValidationError(u'File Error: No shapefile detected in zip.')
    elif len(shpFiles) > 1:
        raise ValidationError(u'File Error: Multiple shapefiles detected in zip.')
    # Create a list of projection files.
    prjFile = [file for file in filenames if file[len(file)-3:] == 'prj']
    if len(prjFile) == 0:
        raise ValidationError(u'File Error: No projection file detected.')
    # Use zipfile class' read method to check the contents of a prj file to verify WGS84
    if 'GCS_WGS_1984' not in zipfile.ZipFile(value).read(prjFile[0]):
        raise ValidationError(u'File Error: File does not appear to be in WGS84 GCS.')


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

class uploadFileForm1(forms.Form):
    """
    First file upload form page. Take uploaded file from user and
    associate with a given GPS Group.
    """

    # https://docs.djangoproject.com/en/dev/ref/forms/api/#styling-required-or-erroneous-form-rows
    error_css_class = 'text-error'
    required_css_class = 'text-required'

    file = forms.FileField('File', validators=[validate_shp])

class uploadFileForm2(forms.Form):
    """
    Grab an uploaded file and all manual mappings provided by a user
    """
    def __init__(self, *args, **kwargs):
        # http://stackoverflow.com/questions/987237/adding-a-kwarg-to-a-class
        self.shpPath = kwargs.pop('shpPath', None)
        super(uploadFileForm2, self).__init__(*args, **kwargs)
        self.attributeChoices = get_shpFields(self.shpPath)
        self.fields['group'] = forms.ChoiceField(choices=get_groups(), label='GPS Group')
        self.fields['name'] = forms.ChoiceField(choices=self.attributeChoices, label='Name')
        self.fields['type'] = forms.ChoiceField(choices=self.attributeChoices, required=False, label='Feature Type')
        self.fields['method'] = forms.ChoiceField(choices=self.attributeChoices, required=False, label='Collection Method')
        self.fields['collectDate'] = forms.ChoiceField(choices=self.attributeChoices, required=False, label='Collection Date')
        self.fields['collectTime'] = forms.ChoiceField(choices=self.attributeChoices, required=False, label='Collection Time')
        self.fields['comment'] = forms.ChoiceField(choices=self.attributeChoices, required=False, label='Comment')

    # https://docs.djangoproject.com/en/dev/ref/forms/api/#styling-required-or-erroneous-form-rows
    error_css_class = 'text-error'
    required_css_class = 'text-required'
