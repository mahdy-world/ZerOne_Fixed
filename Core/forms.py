from django import forms
from .models import *

class SystemInfoForm(forms.ModelForm):
    class Meta:
        model = SystemInformation
        fields = '__all__'