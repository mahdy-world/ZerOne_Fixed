from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Factory)
admin.site.register(Payment)
admin.site.register(FactoryInSide)
admin.site.register(FactoryOutSide)