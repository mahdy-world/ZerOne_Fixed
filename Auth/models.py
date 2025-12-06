from django.db import models
from django.contrib.auth.models import AbstractUser
from Core.models import Modules

# Create your models here.
class User(AbstractUser):
    avater = models.ImageField(null=True, blank=True)
    
    # def has_access_to_factory(self):
    #     setting = Modules.objects.all().first()
    #     if setting.factory_active == True:
    #         return True
    #     else:
    #         return False
