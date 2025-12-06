from django.db import models
from datetime import date
from Auth.models import User

# Create your models here.

class WoolSupplier(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الاضافة")
    name = models.CharField(max_length=50, verbose_name="إسم المورد")
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='رقم الهاتف')
    address = models.CharField(max_length=250, verbose_name='العنوان', null=True, blank=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


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

class WoolSupplierQuantity(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ العملية")
    date = models.DateField(null=True, verbose_name="التاريخ", default=date.today)
    supplier = models.ForeignKey(WoolSupplier, on_delete=models.CASCADE, verbose_name="المورد")
    wool_type = models.IntegerField(choices=WOOL_TYPE, verbose_name="نوع الخيط")
    wool_weight = models.FloatField(default=0.0, verbose_name="الوزن بالكيلو")
    wool_price = models.FloatField(default=0.0, verbose_name="سعر الكيلو")
    total_account = models.FloatField(default=0.0, verbose_name="اجمالي الحساب")
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="المسؤول")

    def __str__(self):
        return self.supplier.name


class WoolSupplierPayment(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ العملية")
    date = models.DateField(null=True, verbose_name="التاريخ", default=date.today)
    supplier = models.ForeignKey(WoolSupplier, on_delete=models.CASCADE, verbose_name="المورد")
    value = models.FloatField(default=0.0, verbose_name="المبلغ")
    reason = models.CharField(max_length=250, null=True, blank=True, verbose_name='الوصف/السبب')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="المسؤول")

    def __str__(self):
        return self.supplier.name