from datetime import date

from django.db import models
from Auth.models import User

from Products.models import Product

# Create your models here.

class Factory(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الاضافة")
    name = models.CharField(max_length=50, verbose_name="اسم المصنع")
    hour_price = models.FloatField(null=True, blank=True, verbose_name="حساب الساعه")
    machine_type = models.CharField(null=True, blank=True, max_length=50, verbose_name="نوع المكن")
    machine_count = models.IntegerField(null=True, blank=True, verbose_name="عدد المكن")
    phone = models.CharField(null=True, blank=True, max_length=12, verbose_name="رقم الهاتف")
    active = models.BooleanField(default=True, verbose_name="يعمل")
    start_date = models.DateField(null=True, blank=True, verbose_name="تاريخ البداية", default=date.today)
    deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
class Payment(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الاضافة")
    price = models.FloatField(verbose_name="المبلغ")
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, verbose_name="المصنع")
    recipient = models.CharField(max_length=50, null=True, blank=True, verbose_name="المستلم")
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="المسئول")
    date = models.DateField(null=True, verbose_name="التاريخ", default=date.today)
    
    def __str__(self):
        return self.factory.name
    
WOOL_TYPE = (
    (1,"قطن"),
    (2,"صوف"),
    (3,"عجينة"),
    (4,"سبن"),
    (5,"لكرة"),
    (6,"رمش"),
    (7,"عصب"),
    (8,"بلستر"),
    (9,"استك"),
)    
         

class FactoryOutSide(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ العملية")
    date = models.DateField(null=True, verbose_name="التاريخ", default=date.today)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, verbose_name="المصنع")
    weight = models.FloatField(null=True, verbose_name="الوزن بالكيلو")
    wool_type = models.IntegerField(choices=WOOL_TYPE, null=True, blank=True, verbose_name="نوع الخامة")
    color = models.CharField(null=True, max_length=50, blank=True, verbose_name="اللون")
    percent_loss = models.FloatField(null=True, verbose_name="الهالك (نسبة مؤية)")
    weight_after_loss = models.FloatField(null=True, verbose_name="الوزن بعد الهالك")
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="المسئول")
    
    def __str__(self):
        return self.factory.name


PRODUCT_TYPE = (
    (1,"صدر"),
    (2,"ضهر"),
    (3,"كم"),
    (4,"لياقة"),
)    
     
class FactoryInSide(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ العملية")
    date = models.DateField(null=True, verbose_name="التاريخ", default=date.today)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, verbose_name="المصنع")
    color = models.CharField(null=True, max_length=50, blank=True, verbose_name="اللون")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="الموديل")
    weight = models.FloatField(null=True, verbose_name="الوزن بالكيلو")
    product_weight = models.FloatField(null=True, verbose_name="وزن الموديل جرام")
    product_time = models.FloatField(null=True, verbose_name="زمن الموديل دقائق")
    product_count = models.IntegerField(null=True, verbose_name="عدد الموديل")
    # product_type = models.IntegerField(choices=PRODUCT_TYPE, null=True, blank=True, verbose_name="نوع القطع")
    wool_type = models.IntegerField(choices=WOOL_TYPE, null=True, blank=True, verbose_name="نوع الخامة")
    hour_count = models.FloatField(null=True, verbose_name="عدد الساعات")
    hour_price = models.FloatField(null=True, verbose_name="سعر الساعة")
    total_account = models.FloatField(null=True, verbose_name="اجمالي الحساب")
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="المسئول")
    
    def __str__(self):
        return self.factory.name


Fact_Type = (
    (1, "مصنع مورد"),
    (2, "مصنع مستورد"),
    )


class Supplier(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الاضافة")
    name = models.CharField(max_length=50, verbose_name="إسم المصنع")
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='رقم الهاتف')
    address = models.CharField(max_length=250, verbose_name='العنوان', null=True, blank=True)
    type = models.IntegerField(choices=Fact_Type, default=0, verbose_name="نوع المصنع")
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class SupplierQuantity(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ العملية")
    date = models.DateField(null=True, verbose_name="التاريخ", default=date.today)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="المورد/المستورد")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="الموديل")
    product_count = models.FloatField(default=0, verbose_name="عدد القطع")
    product_price = models.FloatField(default=0.0, verbose_name="سعر القطعة")
    total_account = models.FloatField(default=0.0, verbose_name="اجمالي الحساب")
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="المسؤل")

    def __str__(self):
        return self.supplier.name


class SupplierPayment(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ العملية")
    date = models.DateField(null=True, verbose_name="التاريخ", default=date.today)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="المورد/المستورد")
    value = models.FloatField(default=0.0, verbose_name="المبلغ")
    reason = models.CharField(max_length=250, null=True, blank=True, verbose_name='الوصف/السبب')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="المسؤل")

    def __str__(self):
        return self.supplier.name