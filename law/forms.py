from models import *
from django import forms
from django.forms import ModelForm
import datetime
from tinymce.widgets import TinyMCE

class AddChargeForm(forms.Form):
    label = forms.CharField()
    penal_code = forms.CharField()

class EditChargeForm(ModelForm):
    class Meta:
        model = Charge

class EditAreaForm(ModelForm):
    class Meta:
        model = Area

class EditClassificationForm(ModelForm):
    class Meta:
        model = Classification

class EditConsequenceForm(ModelForm):
    class Meta:
        model = Consequence

class AddClassificationForm(forms.Form):
    label = forms.CharField()
    description = forms.CharField(widget=TinyMCE)

class AddAreaForm(forms.Form):
    label = forms.CharField()

class AddConsequenceForm(forms.Form):
    label = forms.CharField()
    description = forms.CharField(widget=TinyMCE())

