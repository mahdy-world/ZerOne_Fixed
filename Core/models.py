from django.db import models


# Create your models here.

class SystemInformation(models.Model):
    logo = models.ImageField(null=True, blank=True, verbose_name="شعارالنظام")
    name = models.CharField(null=True, max_length=50, verbose_name="اسم النظام")
    type = models.CharField(null=True, max_length=50, verbose_name="نوع النظام")
    manage = models.CharField(null=True, max_length=50, verbose_name="إدارة")
    phone = models.CharField(null=True, max_length=11, verbose_name="هاتف 1")
    phone2 = models.CharField(null=True, blank=True, max_length=11, verbose_name="هاتف 2")
    address = models.CharField(max_length=150, null=True, verbose_name="العنوان")
    geo_site = models.CharField(max_length=150, null=True, blank=True, verbose_name="موقعك الجغرافي")

    def __str__(self):
        return 'معلومات النظام'
    
    
class Modules(models.Model):
    factory_active = models.BooleanField(default=True, verbose_name="تنشيط المصانع")
    product_active = models.BooleanField(default=True, verbose_name="تنشيط المنتجات")
    seller_active = models.BooleanField(default=True, verbose_name="تنشيط التجار")
    worker_active = models.BooleanField(default=True, verbose_name="تنشيط العمال ")
    invoice_active = models.BooleanField(default=True, verbose_name="تنشيط الفواتير ")
    supplier_active = models.BooleanField(default=True, verbose_name="تنشيط الموردين ")
    treasury_active = models.BooleanField(default=True, verbose_name="تنشيط الخزائن")
    wool_active = models.BooleanField(default=True, verbose_name="تنشيط الخيط")
    stop_date = models.DateField(null=True, blank=True, verbose_name="فترة تجريبية")

    def __str__(self):
        return 'عناصر النظام'


class Backup(models.Model):
    backup_date = models.DateField(null=True)

    def __str__(self):
        return f"تاريخ النسخ: {self.backup_date} "