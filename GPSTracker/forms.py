__author__ = 'matt'
from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()