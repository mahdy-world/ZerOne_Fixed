from django.db import models
from datetime import datetime
from Auth.models import User

# Create your models here.
# class Color(models.Model):
#     created = models.DateTimeField(auto_now_add =True, verbose_name="تاريخ الاضافة")
#     name = models.CharField(max_length=50 , verbose_name="اسم اللون")
#     code = models.CharField(max_length=20, verbose_name="كود اللون")
#
#     def __str__(self):
#         return self.name


CATEGORY= (
    ('', "------------"),
    (1, "شبابي"),
    (2, "حريمي"),
    (3, "اطفالي اولادي"),
    (4, "اطفالي بناتي"),
    )

SIZE= (
    ('', "------------"),
    (1, "S"),
    (2, "M"),
    (3, "L"),
    (3, "XL"),
    (3, "XXL"),
    )

class Product(models.Model):
    created = models.DateTimeField(auto_now=True, verbose_name="تاريخ الاضافة")
    name = models.CharField(max_length=50, verbose_name="رقم/اسم الموديل")
    # code = models.IntegerField(null=True, blank=True, verbose_name="كود الموديل")
    image = models.ImageField(null=True, blank=True, verbose_name="صورة الموديل")
    weight = models.FloatField(null=True, blank=True,  verbose_name="وزن الموديل")
    time = models.FloatField(null=True, blank=True,  verbose_name="زمن الموديل")
    cost = models.FloatField(null=True, blank=True, max_length=15, verbose_name="التكلفة")
    price = models.FloatField(null=True, blank=True, verbose_name="سعر البيع")
    # color = models.ForeignKey(Color, null=True,  on_delete=models.SET_NULL, verbose_name= "اللون")
    size = models.IntegerField(choices=SIZE, default=0, null=True, blank=True, verbose_name="المقاس")
    category = models.IntegerField(choices=CATEGORY, default=0, null=True, blank=True, verbose_name="التصنيف")
    quantity = models.IntegerField(null=True, blank=True, verbose_name="الكمية")
    deleted = models.BooleanField(default=False)
    
    # To create random code for product
    # def save(self, **kwargs):
    #     if not self.code:
    #         self.code = randint(10000, 99999)
    #     return super(Product, self).save(**kwargs)   
    
    def __str__(self):
        return self.name


Balance_Type = (
    (1, "للتاجر"),
    (2, "علي التاجر"),
    )

Paid_Type = (
    (1, "التاجر يدفع لك"),
    (2, "أنت تدفع للتاجر"),
    )

class ProductSellers(models.Model):
    name = models.CharField(max_length=250, verbose_name='اسم التاجر')
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='رقم الهاتف')
    address = models.CharField(max_length=250, verbose_name='العنوان', null=True, blank=True)
    nation_no = models.CharField(max_length=14, verbose_name='الرقم القومي', null=True, blank=True)
    initial_balance_debit = models.FloatField(default=0, verbose_name='القيمة الافتتاحية')
    initial_balance_type = models.IntegerField(choices=Balance_Type, default=0, verbose_name="نوع القيمة الافتتاحية")
    deleted = models.BooleanField(default=False, verbose_name='حذف')
    agreement = models.CharField(max_length=500, verbose_name='اتفاق مسبق', null=True, blank=True)

    def __str__(self):
        return self.name


class SellerPayments(models.Model):
    seller = models.ForeignKey(ProductSellers, on_delete=models.CASCADE, null=True, verbose_name='التاجر')
    paid_value = models.FloatField(default=0.0, verbose_name='القيمة المدفوعة')
    paid_reason = models.CharField(max_length=250, null=True, blank=True, verbose_name='الوصف/السبب')
    paid_type = models.IntegerField(choices=Paid_Type, default=0, verbose_name="نوع الدفع")
    date = models.DateTimeField(default=datetime.now(), verbose_name='التاريخ')
    op = models.BooleanField(null=True, default=False)

    def __str__(self):
        return self.seller