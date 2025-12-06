from django import forms
from .models import *

class SystemInfoForm(forms.ModelForm):
    class Meta:
        model = SystemInformation
        fields = '__all__'
        
class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = '__all__'
        widgets = {
            'color_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'color_name'}),
            'color_hex_code': forms.TextInput(attrs={'class': 'form-control', 'type':'color', 'id':'color_hex_code'}),
        }
        
        
class ExpensessTypeCreateForm(forms.ModelForm):
    class Meta:
        model = ExpnsessType
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'name'}),
        }

class ExpensessForm(forms.ModelForm):
    class Meta:
        model = Expnsess
        fields = ['expnsess_date', 'expnsess_type', 'expnsess_amount', 'expnsess_details', 'expnsess_notes']
        widgets = {
            'expnsess_date': forms.DateInput(attrs={'class': 'form-control', 'id': 'expnsess_date', 'type': 'date'}),
            'expnsess_type': forms.Select(attrs={'class': 'form-control', 'id':'expnsess_type'}),
            'expnsess_amount': forms.NumberInput(attrs={'class': 'form-control', 'min':'1', 'id':'expnsess_amount'}),
            'expnsess_details': forms.TextInput(attrs={'class': 'form-control', 'id':'expnsess_details'}),
            'expnsess_notes': forms.TextInput(attrs={'class': 'form-control', 'id':'expnsess_notes'}),
            'admin' : forms.Select(attrs={'class':'form-control',  'placeholder':'المسئول...', 'id':'admin'}),

        }
