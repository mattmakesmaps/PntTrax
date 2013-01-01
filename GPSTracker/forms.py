__author__ = 'matt'
from django import forms
from GPSTracker.models import Group

def get_groups():
    """Return groups for a choice list"""
    group_list = Group.objects.all()
    group_choice = []
    for group in group_list:
        group_choice.append((group.id, group.name))
    return group_choice

class UploadFileForm1(forms.Form):
    """
    First file upload form page. Take uploaded file from user and
    associate with a given GPS Group.
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
