from django import forms

from Wool.models import WoolReturn
from .models import *

class FactoryForm(forms.ModelForm):
    class Meta:
        model = Factory
        exclude = ['deleted']
        widgets = {
            'name' : forms.TextInput(attrs={'class':'form-control'}),
            'hour_price' : forms.NumberInput(attrs={'class':'form-control', 'min':0}),
            'machine_type' : forms.TextInput(attrs={'class':'form-control'}),
            'machine_count' : forms.NumberInput(attrs={'class':'form-control', 'min':0}),
            'phone' : forms.TextInput(attrs={'class':'form-control'}),
            'start_date' : forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
            'active' : forms.CheckboxInput(attrs={'class':'form-control'}),
            
        }
        
class FactoryDeleteForm(forms.ModelForm):
    class Meta:
        fields = ['deleted']
        model = Factory
        widgets = {
            'deleted' : forms.HiddenInput()
        }        
        
        
class FactoryPaymentForm(forms.ModelForm):
    class Meta:
        fields = ['date', 'price', 'admin', 'recipient']
        model = Payment
        widgets = {
            'date' : forms.TextInput(attrs={'type':'date', 'class':'form-control',  'placeholder':'تاريخ السحب...', 'id':'date'}),
            'price' : forms.NumberInput(attrs={ 'class':'form-control', 'placeholder':'المبلغ...', 'id':'price'}),
            'admin' : forms.Select(attrs={'class':'form-control',  'placeholder':'المسئول...', 'id':'admin'}),
            'recipient' : forms.TextInput(attrs={'class':'form-control',  'placeholder':'المستلم...', 'id':'recipient'}),
        }
        
# factory returned form 
class RefundForm(forms.ModelForm):
    class Meta:
        fields = ['date', 'item_count', 'admin', 'product', 'item_price', 'total_price', 'returned_details']
        model = FactoryReturned
        widgets = {
            'date' : forms.TextInput(attrs={'type':'date', 'class':'form-control',  'placeholder':'تاريخ السحب...', 'id':'date'}),
            'item_count' : forms.NumberInput(attrs={ 'class':'form-control', 'placeholder':'عدد القطع...', 'id':'item_count'}),
            'admin' : forms.Select(attrs={'class':'form-control',  'placeholder':'المسئول...', 'id':'admin'}),
            'returned_details' : forms.TextInput(attrs={'class':'form-control',  'placeholder':'التفاصيل...', 'id':'returned_details'}),
            'product' : forms.Select(attrs={'class':'form-control',  'placeholder':'الموديل...', 'id':'returned_product'}),
            'item_price' : forms.NumberInput(attrs={ 'class':'form-control', 'placeholder':'سعر القطعة...', 'id':'item_price'}),
            'total_price' : forms.NumberInput(attrs={ 'class':'form-control', 'placeholder':'اجمالي السعر...', 'id':'total_price'}),

        }



class FactoryPaymentReportForm(forms.Form):
    from_date = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type':'date',
        'name':'form_date',
        'id':'from_date',
        'class':'form-control',
        'placeholder':'من ...'}),                       
        label= 'من',
        )
         
    to_date = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type':'date',
        'name':'to_date',
        'id':'to_date',
        'class':'form-control',
        'placeholder':'الي ...'}),
        label= 'الي',
        )     



        
class FactoryOutSideForm(forms.ModelForm):
    class Meta:
        fields = ['date', 'weight','wool', 'wool_count_item',  'percent_loss', 'weight_after_loss' ]
        model = FactoryOutSide
        widgets = {
            'date' : forms.TextInput(attrs={'type':'date', 'class':'form-control',  'placeholder':'تاريخ الخروج...', 'id':'datee'}),
            'wool' : forms.Select(attrs={'class':'form-control',  'placeholder':'الخامة...', 'id':'wool'}),
            'wool_count_item' : forms.NumberInput(attrs={'class':'form-control', 'min':'1', 'placeholder':'عددالشكاير...', 'id':'wool_count_item'}),
            'weight' : forms.NumberInput(attrs={'class':'form-control', 'min':'1', 'placeholder':'الوزن...', 'id':'weight'}),
            # 'color' : forms.Select(attrs={'class':'form-control', 'placeholder':'اللون...', 'id':'color'}),
            'percent_loss' : forms.NumberInput(attrs={'class':'form-control', 'min':'1', 'placeholder':'نسبة الهالك...', 'id':'percent_loss'}),
            'weight_after_loss' : forms.NumberInput(attrs={'class':'form-control', 'min':'1', 'placeholder':'الوزن بعدالهالك...', 'id':'weight_after_loss'}),
        }
        
        
class FactoryInSideForm(forms.ModelForm):
    class Meta:
        fields = ['date', 'weight', 'color', 'product', 'product_weight', 
                  'product_time', 'product_count','hour_count', 'hour_price',
                  'total_account', 'wool_type']
        model = FactoryInSide
        widgets = {
            'date' : forms.TextInput(attrs={'type':'date', 'class':'form-control',  'placeholder':'تاريخ الاستلام...', 'id':'date_inside'}),
            'weight' : forms.NumberInput(attrs={ 'class':'form-control', 'min':'1', 'placeholder':'الوزن المستلم...', 'id':'weight_inside'}),
            'color' : forms.Select(attrs={ 'class':'form-control', 'placeholder':' اللون...', 'id':'color_inside'}),
            'wool_type' : forms.Select(attrs={'class':'form-control',  'placeholder':'نوع الخامة...', 'id':'wool_type_inside'}),
            'product' : forms.Select(attrs={ 'class':'form-control', 'placeholder':' المنتج...', 'id':'product'}),
            'product_weight' : forms.NumberInput(attrs={ 'class':'form-control', 'min':'1', 'placeholder':' وزن القطعة...', 'id':'product_weight'}),
            'product_time' : forms.NumberInput(attrs={ 'class':'form-control', 'min':'1', 'placeholder':' وقت القطعة...', 'id':'product_time'}),
            'product_count' : forms.NumberInput(attrs={ 'class':'form-control', 'min':'1', 'placeholder':'  عدد القطع...', 'id':'product_count'}),
            'hour_count' : forms.NumberInput(attrs={ 'class':'form-control', 'min':'1', 'placeholder':'  عدد الساعات...', 'id':'hour_count'}),
            'hour_price' : forms.NumberInput(attrs={ 'class':'form-control', 'min':'1', 'placeholder':'سعر الساعة...', 'id':'hour_price'}),
            'total_account' : forms.NumberInput(attrs={ 'class':'form-control', 'min':'1', 'placeholder':'اجمالي الحساب...', 'id':'total_account'}),
        }


###########################################################


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        exclude = ['deleted', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'phone': forms.TextInput(attrs={'class':'form-control'}),
            'address': forms.TextInput(attrs={'class':'form-control'}),
        }

class SupplierDeleteForm(forms.ModelForm):
    class Meta:
        fields = ['deleted']
        model = Supplier
        widgets = {
            'deleted' : forms.HiddenInput()
        }


class SupplierQuantityForm(forms.ModelForm):
    class Meta:
        model = SupplierQuantity
        fields = ['date', 'product', 'product_count', 'product_price', 'total_account']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'id': 'date', 'type':'date'}),
            'product': forms.Select(attrs={'class': 'form-control', 'id': 'product'}),
            'product_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'product_count'}),
            'product_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'product_price'}),
            'total_account': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'total_account', 'readonly': 'readonly'}),
        }


class SupplierPaymentForm(forms.ModelForm):
    class Meta:
        model = SupplierPayment
        fields = ['date', 'value', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'id': 'date', 'type':'date'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'value'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'id': 'reason'}),
        }

class ProductQuantityInsideForm(forms.ModelForm):
    class Meta:
        model = ProductQuantityInside
        fields = ['date', 'factory_item', 'product_count', 'product_color']
        widgets = {
            'date' : forms.TextInput(attrs={'type':'date', 'class':'form-control',  'placeholder':'التاريخ...', 'id':'date'}),
            'factory_item': forms.Select(attrs={'class':'form-control', 'id':'factory_item'}),
            'product_count': forms.NumberInput(attrs={'class':'form-control', 'min': '1', 'id': 'product_count'}),
            'product_color': forms.Select(attrs={'class':'form-control', 'id': 'product_color'}),
        }


class FactoryReturnWool(forms.ModelForm):
    class Meta:
        fields = ['date', 'wool_name', 'wool_retuern_color', 'wool_return_weight']
        model = WoolReturn
        widgets = {
            'date' : forms.TextInput(attrs={'type':'date', 'class':'form-control',  'placeholder':'تاريخ الخروج...', 'id':'wool_date'}),
            'wool_name' : forms.TextInput(attrs={'class':'form-control',  'placeholder':'الخامة...', 'id':'wool_name'}),
            'wool_retuern_color' : forms.Select(attrs={'class':'form-control',  'placeholder':'اللون...', 'id':'wool_color'}),
            'wool_return_weight' : forms.NumberInput(attrs={'class':'form-control', 'min':'1', 'placeholder':'الوزن...', 'id':'wool_weight'}),
        }
        