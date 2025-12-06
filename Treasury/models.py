from django.db.models.signals import post_save
from django.db import models
from django.dispatch import receiver
from Auth.models import User
from datetime import date


class Treasury(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الخزنة")
    date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الاضافة")
    balance = models.FloatField(default=0.00, verbose_name="رصيد الخزنة")
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

OPERATION_TYPE = (
    (1, "اضافة رصيد"),
    (2, "سحب رصيد")
)

class TreasuryOperation(models.Model):
    treasury = models.ForeignKey(Treasury, on_delete=models.CASCADE,null=True, blank=True, verbose_name="الخزنة")
    operation_type = models.IntegerField(choices=OPERATION_TYPE, default=0, verbose_name="نوع العملية")
    operation_value = models.FloatField(default=0.0, verbose_name="قيمة العملية")
    operation_description = models.TextField(max_length=200, null=True, blank=True, verbose_name="وصف العملية")
    operation_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="انشاء بواسطة")
    operation_date = models.DateTimeField(default=date.today, verbose_name="تاريخ العملية")
    deleted_operation = models.BooleanField(default=False)

    def __str__(self):
        return self.treasury.name
    

# signals function to create operation when user created new treasury 
@receiver(post_save, sender=Treasury)
def create_treasury_operatoin(sender, instance, created, **kwargs):
    if created:
        import inspect
        for frame_record in inspect.stack():
            if frame_record[3] == 'get_response':
                request = frame_record[0].f_locals['request']
                break
        else:
            request = None

        if instance.balance > 0:
            TreasuryOperation.objects.create(
                treasury=instance,
                operation_type=1,
                operation_value=instance.balance,
                operation_description="قيمة افتتاحية",
                operation_user=request.user
                )
