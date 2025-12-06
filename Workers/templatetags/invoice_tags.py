# from django import template
# from django.db.models import Sum
# import pyqrcode
# from django.db.models import F

# from Workers.models import WorkerAttendance, WorkerProduction, WorkerPayment, Worker

# register = template.Library()
# from Invoices.models import *


# @register.simple_tag(name='worker_total_price')
# def worker_total_price(worker_id, worker_type):
#     if woker_type == 5:
#         worker_total = WorkerAttendance.objects.filter(id=worker_id).aggregate(sum=Sum(F('quantity') * F('unit'))).get('sum')
#     if worker_total:
#         worker_total = float(worker_total)
#     else:
#         worker_total = 0
#     return float(worker_total)