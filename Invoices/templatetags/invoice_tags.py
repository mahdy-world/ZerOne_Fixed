from django import template
from django.db.models import Sum
import pyqrcode
from django.db.models import F

register = template.Library()
from Invoices.models import *

@register.simple_tag(name='invoice_products')
def invoice_products(inv_id):
    return InvoiceItem.objects.filter(invoice__id=inv_id)


@register.simple_tag(name='invoice_products_val')
def invoice_products_val(inv_id):
    return InvoiceItem.objects.filter(invoice__id=inv_id).aggregate(sum=Sum('total_price')).get('sum')


@register.simple_tag(name='invoice_saved')
def invoice_saved(inv_id):
    return Invoice.objects.filter(id=inv_id, saved=True, close=False)


@register.simple_tag(name='invoice_closed')
def invoice_closed(inv_id):
    return Invoice.objects.filter(id=inv_id, saved=True, close=True)


@register.simple_tag(name='profit_decimal')
def Profit_Decimal(num):
    number = num

    if number:
        numbe = "{:g}".format(number)
    else:
        numbe = number

    if '.' in str(numbe):
        numb = str(numbe).split('.')
        if len(numb[1]) == 1:
            numm = "{:.1f}".format(float(numbe))
        else:
            numm = "{:.2f}".format(float(numbe))
    else:
        numm = numbe

    return numm


@register.simple_tag(name='qrcode')
def qrcode(*args):
    value = ''
    for i in args:
        value = value + '\n' + str(i)
    code = pyqrcode.create(value, encoding='utf-8')
    image_as_str = code.png_as_base64_str(scale=5)

    return image_as_str


@register.simple_tag(name='invoice_products_count')
def invoice_products_count(inv_id):
    products_count = InvoiceItem.objects.filter(invoice__id=inv_id).aggregate(sum=Sum(F('quantity') * F('unit'))).get('sum')
    if products_count:
        products_count = int(products_count)
    else:
        products_count = 0
    return int(products_count)