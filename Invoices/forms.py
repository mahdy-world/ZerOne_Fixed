from django import forms
from .models import *

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['date', 'seller']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'seller': forms.Select(attrs={'class': 'form-control', 'id': 'seller_s2', 'style': 'width:100%'}),
        }


class InvoiceForm2(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['date', 'customer']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class InvoiceSaveForm(forms.ModelForm):
    class Meta:
        model = Invoice
        # fields = ['old_value', 'total', 'discount', 'return_value', 'paid_value', 'overall', 'comment']
        fields = ['old_value', 'total', 'discount', 'paid_value', 'overall', 'comment']
        widgets = {
            'total': forms.NumberInput(attrs={'class': 'form-control', 'id': 'inv_total', 'readonly': 'readonly', 'min':0}),
            'old_value': forms.NumberInput(attrs={'class': 'form-control', 'id': 'inv_old_value', 'readonly': 'readonly'}),
            'overall': forms.HiddenInput(attrs={'class': 'form-control', 'id': 'inv_overall', 'readonly': 'readonly', 'min':0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discount'].widget.attrs = {'min': '0', 'max': self['total'].value(), 'id': 'inv_discount'}


class InvoiceSaveForm2(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['old_value', 'total', 'discount', 'overall', 'comment']
        widgets = {
            'total': forms.NumberInput(attrs={'class': 'form-control', 'id': 'inv_total', 'readonly': 'readonly', 'min':0}),
            'old_value': forms.NumberInput(attrs={'class': 'form-control', 'id': 'inv_old_value', 'readonly': 'readonly'}),
            'overall': forms.HiddenInput(attrs={'class': 'form-control', 'id': 'inv_overall', 'readonly': 'readonly', 'min':0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discount'].widget.attrs = {'min': '0', 'max': self['total'].value(), 'id': 'inv_discount'}


class InvoiceSaveForm3(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['total', 'discount', 'overall', 'comment']
        widgets = {
            'total': forms.NumberInput(attrs={'class': 'form-control', 'id': 'inv_total', 'readonly': 'readonly', 'min':0}),
            'overall': forms.HiddenInput(attrs={'class': 'form-control', 'id': 'inv_overall', 'readonly': 'readonly', 'min':0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discount'].widget.attrs = {'min': '0', 'max': self['total'].value(), 'id': 'inv_discount'}


class InvoiceBackForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['saved']
        widgets = {
            'saved': forms.HiddenInput(),
        }


class InvoiceDeleteForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['deleted']
        widgets = {
            'deleted': forms.HiddenInput(),
        }

class InvoiceCloseForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['close']
        widgets = {
            'close': forms.HiddenInput(),
        }

class InvoiceProductsForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['item', 'unit_price', 'quantity', 'unit', 'total_price']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control', 'id': 'item'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'quantity'}),
            'unit': forms.Select(attrs={'class': 'form-control', 'id': 'unit'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'unit_price'}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'total_price', 'readonly': 'readonly'}),
        }


# class InvoiceItemProductsForm(forms.ModelForm):
#     class Meta:
#         model = InvoiceItemDetails
#         fields = ['item', 'unit_price', 'quantity', 'unit', 'total_price']
#         widgets = {
#             'item': forms.Select(attrs={'class': 'form-control', 'id': 'item'}),
#             'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'quantity'}),
#             'unit': forms.Select(attrs={'class': 'form-control', 'id': 'unit'}),
#             'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'unit_price', 'readonly': 'readonly'}),
#             'total_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'total_price', 'readonly': 'readonly'}),
#         }


class InvoiceProductsFormUpdate(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['item', 'unit_price', 'quantity', 'unit', 'total_price']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control', 'id': 'item', 'readonly': 'readonly'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'quantity'}),
            'unit': forms.Select(attrs={'class': 'form-control', 'id': 'unit'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'unit_price'}),
            'total_price': forms.HiddenInput(attrs={'class': 'form-control', 'min': '1', 'id': 'total_price', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super(InvoiceProductsFormUpdate, self).__init__(*args, **kwargs)
        self.fields['item'].empty_label = None


class InvoiceProductsDeleteForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['deleted']
        widgets = {
            'deleted': forms.HiddenInput(),
        }