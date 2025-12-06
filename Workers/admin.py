from django.contrib import admin

from Workers.models import *

# Register your models here.
admin.site.register(Worker)
admin.site.register(WorkerPayment)
admin.site.register(WorkerAttendance)
admin.site.register(WorkerProduction)