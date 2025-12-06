from django import forms
from .models import *


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['deleted', ]
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'image': forms.FileInput(attrs={'class':'form-control'}),
            'weight': forms.NumberInput(attrs={'class':'form-control', 'min':0}),
            'time': forms.NumberInput(attrs={'class':'form-control', 'min':0}),
            'cost': forms.NumberInput(attrs={'class':'form-control', 'min':0}),
            'price': forms.NumberInput(attrs={'class':'form-control', 'min':0}),
            # 'color': forms.Select(attrs={'class':'form-control'}),
            'size': forms.Select(attrs={'class':'form-control'}),
            'category': forms.Select(attrs={'class':'form-control'}),
            'quantity': forms.NumberInput(attrs={'class':'form-control', 'min':0}),
        }


class ProductFormUpdate(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['deleted',]
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'image': forms.FileInput(attrs={'class':'form-control'}),
            'weight': forms.NumberInput(attrs={'class':'form-control', 'min':0}),
            'time': forms.NumberInput(attrs={'class': 'form-control', 'min':0}),
            'cost': forms.NumberInput(attrs={'class':'form-control', 'min':0}),
            'price': forms.NumberInput(attrs={'class':'form-control', 'min':0}),
            # 'color': forms.Select(attrs={'class':'form-control'}),
            'size': forms.Select(attrs={'class':'form-control'}),
            'category': forms.Select(attrs={'class':'form-control'}),
            'quantity': forms.NumberInput(attrs={'class':'form-control', 'readonly':'readonly', 'min':0}),
        }


class ProductDeleteForm(forms.ModelForm):
    class Meta:
        fields = ['deleted']
        model = Product
        widgets = {
            'deleted' : forms.HiddenInput()
        }


class ProductQuantityForm(forms.ModelForm):
    add_quant = forms.IntegerField(label='اضافة كمية جديدة')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['add_quant'].widget.attrs.update({'class': 'form-control', 'placeholder': 'ادخل كمية هنا ..', 'min':1})
        self.fields['quantity'].label = 'الكمية الموجودة'

    class Meta:
        model = Product
        fields = ['quantity', 'add_quant']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'min':0}),
        }


class ProductQuantityMinusForm(forms.ModelForm):
    add_quant = forms.IntegerField(label='خصم كمية')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['add_quant'].widget.attrs.update({'class': 'form-control', 'placeholder': 'ادخل كمية هنا ..', 'min':1})
        self.fields['quantity'].label = 'الكمية الموجودة'

    class Meta:
        model = Product
        fields = ['quantity', 'add_quant']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'min':0}),
        }


class ProductSellerForm(forms.ModelForm):
    class Meta:
        model = ProductSellers
        exclude = ['deleted']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'phone': forms.TextInput(attrs={'class':'form-control'}),
            'address': forms.TextInput(attrs={'class':'form-control'}),
            'nation_no': forms.TextInput(attrs={'class':'form-control'}),
            'initial_balance_debit': forms.NumberInput(attrs={'class':'form-control', 'min':0}),
            'initial_balance_type': forms.Select(attrs={'class':'form-control'}),
            'agreement': forms.TextInput(attrs={'class':'form-control'}),
        }


class ProductSellerFormUpdate(forms.ModelForm):
    class Meta:
        model = ProductSellers
        exclude = ['deleted', 'initial_balance_debit', 'initial_balance_type']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'phone': forms.TextInput(attrs={'class':'form-control'}),
            'address': forms.TextInput(attrs={'class':'form-control'}),
            'nation_no': forms.TextInput(attrs={'class':'form-control'}),
            'agreement': forms.TextInput(attrs={'class':'form-control'}),
        }


class ProductSellerDeleteForm(forms.ModelForm):
    class Meta:
        fields = ['deleted']
        model = Product
        widgets = {
            'deleted': forms.HiddenInput()
        }


class ProductSellerPaymentForm(forms.ModelForm):
    class Meta:
        model = SellerPayments
        fields = ['paid_value', 'paid_reason']
        widgets = {
            'paid_value': forms.NumberInput(attrs={'class': 'form-control', 'min':1}),
            'paid_reason': forms.TextInput(attrs={'class': 'form-control', 'id': 'paid_reason'}),
        }
        
