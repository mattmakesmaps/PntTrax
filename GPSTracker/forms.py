__author__ = 'matt'
from fiona import collection
from django import forms
from django.core.exceptions import ValidationError
from .models import Group

def validate_zip(value):
    """Raise ValidationError if input is not a zip file."""
    # application/x-zip-compressed
    if value.content_type not in ['application/x-zip-compressed','application/zip']:
        raise ValidationError(u'ERROR: Not a valid .zip file.')

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

    file = forms.FileField('File', validators=[validate_zip])

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
