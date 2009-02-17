from models import *
from django import forms
import datetime

class AddChargeForm(forms.Form):
    label = forms.CharField()
    penal_code = forms.CharField()
