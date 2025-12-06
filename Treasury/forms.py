from django import forms
from .models import *


class TreasuryForm(forms.ModelForm):
    class Meta:
        model = Treasury
        exclude = ['deleted']
        widgets = {
            'name' : forms.TextInput(attrs={'class':'form-control'}),
            'balance' : forms.NumberInput(attrs={'class':'form-control', 'min':0}),
        }


class TreasuryFormUpdate(forms.ModelForm):
    class Meta:
        model = Treasury
        fields = ['name']
        widgets = {
            'name' : forms.TextInput(attrs={'class':'form-control'}),
        }


class TreasuryDeleteForm(forms.ModelForm):
    class Meta:
        fields = ['deleted']
        model = Treasury
        widgets = {
            'deleted' : forms.HiddenInput()
        }        


class TreasuryOperationForm(forms.ModelForm):
    class Meta:
        fields = ['operation_date', 'operation_value', 'operation_description']
        model = TreasuryOperation
        widgets = {
            'operation_date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'تاريخ العملية...'}),
            'operation_value' : forms.NumberInput(attrs={'class':'form-control', 'min':1}),
            'operation_description' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'تفاصيل العملية......'}),
        }

    def __init__(self, *args, **kwargs):
        treasury_id = kwargs.pop('treasury_id', None)
        super(TreasuryOperationForm, self).__init__(*args, **kwargs)
        self.fields['operation_date'].widget.attrs['min'] = Treasury.objects.get(id=treasury_id).date.date()


class TreasuryOperationDeleteForm(forms.ModelForm):
    class Meta:
        fields = ['deleted_operation']
        model = TreasuryOperation
        widgets = {
            'deleted_operation' : forms.HiddenInput()
        }        

