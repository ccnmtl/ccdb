from models import Charge, Area, Classification, Consequence
from django import forms
from django.forms import ModelForm


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
    description = forms.CharField(widget=forms.Textarea)


class AddAreaForm(forms.Form):
    label = forms.CharField()


class AddConsequenceForm(forms.Form):
    label = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
