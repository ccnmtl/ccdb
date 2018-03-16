from ccdb.law.models import Charge, Area, Classification, Consequence
from django import forms
from django.forms import ModelForm


class AddChargeForm(forms.Form):
    label = forms.CharField()
    penal_code = forms.CharField()


class EditChargeForm(ModelForm):
    class Meta:
        model = Charge
        exclude = []


class EditAreaForm(ModelForm):
    class Meta:
        model = Area
        exclude = []


class EditClassificationForm(ModelForm):
    class Meta:
        model = Classification
        exclude = []


class EditConsequenceForm(ModelForm):
    class Meta:
        model = Consequence
        exclude = []


class AddClassificationForm(forms.Form):
    label = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)


class AddAreaForm(forms.Form):
    label = forms.CharField()


class AddConsequenceForm(forms.Form):
    label = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
