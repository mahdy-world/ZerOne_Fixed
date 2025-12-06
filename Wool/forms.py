from django import forms
from .models import *


class WoolSupplierForm(forms.ModelForm):
    class Meta:
        model = WoolSupplier
        exclude = ['deleted']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        
class WoolForm(forms.ModelForm):
    class Meta:
        model = Wool
        exclude = ['wool_user_created']
        widgets = {
            'wool_date': forms.DateInput(attrs={'class': 'form-control', 'id': 'wool_date', 'type': 'date'}),
            'wool_name': forms.TextInput(attrs={'class': 'form-control', 'id':'wool_name'}),
            'wool_type': forms.Select(attrs={'class': 'form-control', 'id':'wool_type'}),
            'wool_company': forms.TextInput(attrs={'class': 'form-control', 'id':'wool_company'}),
            'wool_number': forms.NumberInput(attrs={'class': 'form-control', 'min':'1', 'id':'wool_number'}),
        }

class WoolSupplierDeleteForm(forms.ModelForm):
    class Meta:
        fields = ['deleted']
        model = WoolSupplier
        widgets = {
            'deleted': forms.HiddenInput()
        }


class WoolDeleteForm(forms.ModelForm):
    class Meta:
        fields = ['wool_name']
        model = Wool
        widgets = {
            'wool_name': forms.HiddenInput()
        }

# form on the supplier details to add new quantity for supplier
class WoolSupplierQuantityForm(forms.ModelForm):
    class Meta:
        model = WoolSupplierQuantity
        fields = ['date', 'wool', 'wool_color', 'wool_item_count','wool_weight', 'wool_price', 'total_account']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'id': 'date', 'type': 'date'}),
            'wool': forms.Select(attrs={'class': 'form-control', 'id': 'wool'}),
            'wool_color': forms.Select(attrs={'class': 'form-control', 'id': 'wool_color'}),
            'wool_item_count': forms.NumberInput(attrs={'class': 'form-control', 'min':'1', 'id': 'wool_item_count'}),
            'wool_weight': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'wool_weight'}),
            'wool_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'wool_price'}),
            'total_account': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'total_account', 'readonly': 'readonly'}),
        }


# form on the wool details to add new quntity on for wool 
class WoolQuantityForm(forms.ModelForm):
    class Meta:
        model = WoolSupplierQuantity
        fields = ['date', 'supplier', 'wool_color', 'wool_item_count','wool_weight', 'wool_price', 'total_account']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'id': 'date', 'type': 'date'}),
            'supplier': forms.Select(attrs={'class': 'form-control', 'id': 'supplier'}),
            'wool_color': forms.Select(attrs={'class': 'form-control', 'id': 'wool_color'}),
            'wool_item_count': forms.NumberInput(attrs={'class': 'form-control', 'min':'1', 'id': 'wool_item_count'}),
            'wool_weight': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'wool_weight'}),
            'wool_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'wool_price'}),
            'total_account': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'total_account', 'readonly': 'readonly'}),
        }


class WoolSupplierPaymentForm(forms.ModelForm):
    class Meta:
        model = WoolSupplierPayment
        fields = ['date', 'value', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'id': 'date', 'type':'date'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'value'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'id': 'reason'}),
        }
