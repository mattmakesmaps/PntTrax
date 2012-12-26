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
        self.fields['gps_group'] = forms.ChoiceField(choices=get_groups())

    # https://docs.djangoproject.com/en/dev/ref/forms/api/#styling-required-or-erroneous-form-rows
    error_css_class = 'text-error'
    required_css_class = 'text-required'

    name_field = forms.CharField()
    type_field = forms.CharField(required=False)
    method_field = forms.CharField(required=False)
    collectDate_field = forms.CharField(required=False)
    comment_field = forms.CharField(required=False)

    file = forms.FileField('File')
