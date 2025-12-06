from django import template
from django.db.models import Sum

register = template.Library()
from Invoices.models import *
from django.db.models import F

@register.simple_tag(name='sellers_debit')
def sellers_debit(seller_id):
    seller = ProductSellers.objects.get(id=seller_id)
    seller_payments_from = SellerPayments.objects.filter(seller__id=seller_id, paid_type=1)
    seller_payments_to = SellerPayments.objects.filter(seller__id=seller_id, paid_type=2)
    if seller:
        initial_debit = seller.initial_balance_debit
    else:
        initial_debit = 0

    if seller_payments_from:
        payments_from = seller_payments_from.aggregate(sum=Sum('paid_value')).get('sum')
    else:
        payments_from = 0

    if seller_payments_to:
        payments_to = seller_payments_to.aggregate(sum=Sum('paid_value')).get('sum')
    else:
        payments_to = 0

    if seller.initial_balance_type == 1:
        sum1 = (payments_from - payments_to) + initial_debit
    else:
        sum1 = (payments_from - payments_to) - initial_debit

    invoices = Invoice.objects.filter(seller=seller, invoice_type=1, saved=True)
    # invoices_return_value = invoices.aggregate(sum=Sum('return_value')).get('sum')
    invoices_return_total = invoices.aggregate(sum=Sum(F('total') - F('discount'))).get('sum')

    # if invoices_return_value:
    #     invoices_return_value = invoices_return_value
    # else:
    #     invoices_return_value = 0

    if invoices_return_total:
        invoices_return_total = invoices_return_total
    else:
        invoices_return_total = 0

    r_invoices = Invoice.objects.filter(seller=seller, invoice_type=2, saved=True)
    r_invoices_return_total = r_invoices.aggregate(sum=Sum(F('total') - F('discount'))).get('sum')

    if r_invoices_return_total:
        r_invoices_return_total = r_invoices_return_total
    else:
        r_invoices_return_total = 0

    # sum2 = invoices_return_total - invoices_return_value - r_invoices_return_total
    sum2 = invoices_return_total - r_invoices_return_total

    total = sum1 - sum2
    return float(total)


@register.simple_tag(name='product_12_quantity')
def product_12_quantity(product_id):
    prod = Product.objects.get(id=product_id)
    if prod.quantity:
        quant = prod.quantity / 12
        if prod.quantity % 12 == 0:
            quant = int(quant)
        else:
            quant = '＋' + str(int(quant))
    else:
        quant = 0
    return quant