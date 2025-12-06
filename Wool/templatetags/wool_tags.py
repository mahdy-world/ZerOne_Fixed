from django import template 
from django.db.models import Sum
from Wool.models import WoolColor, WoolSupplierQuantity
from django.db.models import Sum

register = template.Library()

# function return sum of wool item 
@register.simple_tag(name='color_total')
def color_total(wool_id):
    return WoolColor.objects.filter(wool__id=wool_id).aggregate(sum=Sum('count')).get('sum')

# function return sum of weight total 
@register.simple_tag(name='weight_total')
def weight_total(wool_id):
    return WoolColor.objects.filter(wool_id=wool_id).aggregate(sum=Sum('weight')).get('sum')

# function return sum of weight total 
@register.simple_tag(name='avalibale_color')
def color_avaliable(wool_id):
    return WoolColor.objects.filter(wool_id=wool_id).values('color__color_name').annotate(wcount=Sum('count'))

