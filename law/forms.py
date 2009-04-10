from models import *
from django import forms
import datetime
from tinymce.widgets import TinyMCE

class AddChargeForm(forms.Form):
    label = forms.CharField()
    penal_code = forms.CharField()

class AddClassificationForm(forms.Form):
    label = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)

class AddAreaForm(forms.Form):
    label = forms.CharField()

class AddConsequenceForm(forms.Form):
    label = forms.CharField()
    description = forms.CharField(widget=TinyMCE())

