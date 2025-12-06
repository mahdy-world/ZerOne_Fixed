import django
from django.utils import timezone
from django.db import models

from Auth.models import User
from Products.models import Product

# Create your models here.

WORKER_TYPE = (
    (5, "عامل يوميه"),
    (6, "عامل انتاج"),
)

class Worker(models.Model):
    name = models.CharField(max_length=30, verbose_name="اسم العامل")
    image = models.ImageField(verbose_name="صورة العامل", null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True, verbose_name="رقم الموبيل")
    worker_type = models.IntegerField(choices=WORKER_TYPE, null=True, verbose_name="نوع العامل")
    day_cost = models.FloatField(default=0, null=True, verbose_name="التكلفة (*حساب اليومية في حالة عامل اليومية *حساب القطعة في حالة عامل الانتاج)")
    deleted = models.BooleanField(default=False, verbose_name="حذف")
    
    def __str__(self):
        return self.name
    
    
HOUR_COUNT = (
    (1, "6"),
    (2, "8"),
    (3, "12"),
    (4, "18"),
    (5, "غياب"),
)

class WorkerAttendance(models.Model):
    date = models.DateField(verbose_name="تاريخ الحضور", default=django.utils.timezone.now())
    day = models.CharField(max_length=30, verbose_name="اليوم")
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE,verbose_name="العامل")    
    hour_count = models.IntegerField(choices=HOUR_COUNT, null=True, verbose_name="عدد الساعات")
    attend = models.BooleanField(default=0, verbose_name="حضر")
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="المسئول")
    
    def __str__(self):
        return self.worker.name
    
class WorkerPayment(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الاضافة")
    date = models.DateField(verbose_name="تاريخ السحب", default=django.utils.timezone.now())
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, verbose_name=" العامل") 
    price = models.FloatField(verbose_name="المبلغ")
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name="وصف")
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="المسئول")

    def __str__(self):
        return self.worker.name

class WorkerProduction(models.Model):
    date = models.DateField(verbose_name="تاريخ الاستلام", default=django.utils.timezone.now())
    day = models.CharField(max_length=30, verbose_name="اليوم")
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, verbose_name="العامل")
    quantity = models.FloatField(default=0, verbose_name="الكمية بالقطعة")
    price = models.FloatField(default=0, verbose_name="فئة السعر")
    total = models.FloatField(default=0, verbose_name="الإجمالي")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name="المنتج", null=True, blank=True)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="المسئول")
    
    def __str__(self):
        return self.worker.name