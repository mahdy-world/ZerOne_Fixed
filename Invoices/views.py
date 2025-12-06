import json

from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import *
import weasyprint
from .forms import *
from django.contrib import messages
from datetime import datetime
from django.template.loader import render_to_string
from django.http import HttpResponse
from Core.models import *
from Products.templatetags.products_tags import sellers_debit as SellerDebit
# Create your views here.


class InvoiceList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Invoice
    paginate_by = 12

    def get_queryset(self):
        queryset = self.model.objects.filter(deleted=False, invoice_type=int(self.kwargs['type'])).order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['type'] = self.kwargs['type']
        context['count'] = self.model.objects.filter(deleted=False, invoice_type=int(self.kwargs['type'])).count()
        return context


class InvoiceTrashList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Invoice
    paginate_by = 12

    def get_queryset(self):
        queryset = self.model.objects.filter(deleted=True, invoice_type=int(self.kwargs['type'])).order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'trash'
        context['type'] = self.kwargs['type']
        context['count'] = self.model.objects.filter(deleted=True, invoice_type=int(self.kwargs['type'])).count()
        return context


class InvoiceCreate(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = Invoice
    # form_class = InvoiceForm
    def get_form_class(self, **kwargs):
        if int(self.kwargs['type']) == 1 or int(self.kwargs['type']) == 2:
            form_class_name = InvoiceForm
        else:
            form_class_name = InvoiceForm2
        return form_class_name
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if int(self.kwargs['type']) == 1:
            context['title'] = 'فاتورة مبيعات'
        elif int(self.kwargs['type']) == 2:
            context['title'] = 'فاتورة مرتجع مبيعات'
        else:
            context['title'] = 'فاتورة قطاعي'
        context['message'] = 'create'
        context['action_url'] = reverse_lazy('Invoices:InvoiceCreate', kwargs={'type': self.kwargs['type']})
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class=self.form_class)
        if int(self.kwargs['type']) == 1 or int(self.kwargs['type']) == 2:
            form.fields['seller'].queryset = ProductSellers.objects.filter(deleted=False)
        return form

    def form_valid(self, form):
        form.save()
        obj = form.save(commit=False)
        myform = Invoice.objects.get(id=obj.id)
        myform.creator = self.request.user
        myform.invoice_type = int(self.kwargs['type'])
        myform.save()
        return redirect('Invoices:InvoiceDetail', pk=myform.id)

    def get_success_url(self, **kwargs):
        messages.success(self.request, "تم اضافة فاتورة مبيعات بنجاح", extra_tags="success")
        return reverse('Invoices:InvoiceDetail', kwargs={'pk': self.object.id})


class InvoiceUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Invoice
    # form_class = InvoiceForm
    def get_form_class(self, **kwargs):
        if int(self.object.invoice_type) == 1 or int(self.object.invoice_type) == 2:
            form_class_name = InvoiceForm
        else:
            form_class_name = InvoiceForm2
        return form_class_name
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if int(self.object.invoice_type) == 1:
            context['title'] = 'تعديل فاتورة مبيعات: ' + str(self.object)
        elif int(self.object.invoice_type) == 2:
            context['title'] = 'تعديل فاتورة مرتجع مبيعات: ' + str(self.object)
        else:
            context['title'] = 'تعديل فاتورة قطاعي: ' + str(self.object)
        context['message'] = 'update'
        context['action_url'] = reverse_lazy('Invoices:InvoiceUpdate', kwargs={'pk': self.object.id})
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class=self.form_class)
        if int(self.object.invoice_type) == 1 or int(self.object.invoice_type) == 2:
            form.fields['seller'].queryset = ProductSellers.objects.filter(deleted=False)
        return form

    def get_success_url(self, **kwargs):
        messages.success(self.request, "تم تعديل فاتورة مبيعات بنجاح", extra_tags="success")
        return reverse('Invoices:InvoiceList', kwargs={'type': self.object.invoice_type})


class InvoiceSave(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Invoice
    # form_class = InvoiceSaveForm
    def get_form_class(self, **kwargs):
        if int(self.object.invoice_type) == 1:
            form_class_name = InvoiceSaveForm
        elif int(self.object.invoice_type) == 2:
            form_class_name = InvoiceSaveForm2
        else:
            form_class_name = InvoiceSaveForm3

        if int(self.object.invoice_type) == 1 or int(self.object.invoice_type) == 2:
            obj = self.object
            obj.old_value = SellerDebit(self.object.seller.id) * -1
            obj.save(update_fields=['old_value'])

        return form_class_name
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حفظ مؤقت للفاتورة: ' + str(self.object)
        context['message'] = 'inv_save'
        context['action_url'] = reverse_lazy('Invoices:InvoiceSave', kwargs={'pk': self.object.id})
        return context

    def get_success_url(self, **kwargs):
        messages.success(self.request, "تم حفظ الفاتورة بنجاح", extra_tags="success")
        return reverse('Invoices:InvoiceDetail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        total = form.cleaned_data.get("total")
        discount = form.cleaned_data.get("discount")
        # return_value = form.cleaned_data.get("return_value")
        paid_value = form.cleaned_data.get("paid_value")
        old_value = form.cleaned_data.get("old_value")
        inv = form.save(commit=False)
        if int(self.object.invoice_type) == 1:
            # inv.overall = float(total) - float(discount) - float(return_value) - float(paid_value) + float(old_value)
            inv.overall = float(total) - float(discount) - float(paid_value) + float(old_value)
        elif int(self.object.invoice_type) == 2:
            inv.overall = float(old_value) - (float(total) - float(discount))
        else:
            inv.overall = float(total) - float(discount)
        form.save()
        myform = Invoice.objects.get(id=self.kwargs['pk'])
        myform.saved = 1
        myform.save()

        return redirect(self.get_success_url())


class InvoiceClose(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Invoice
    form_class = InvoiceCloseForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حفظ نهائي للفاتورة: ' + str(self.object)
        context['message'] = 'close'
        context['action_url'] = reverse_lazy('Invoices:InvoiceClose', kwargs={'pk': self.object.id})
        return context

    def get_success_url(self, **kwargs):
        messages.success(self.request, "تم حفظ الفاتورة بنجاح", extra_tags="success")
        return reverse('Invoices:InvoiceDetail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        myform = Invoice.objects.get(id=self.kwargs['pk'])
        myform.close = 1
        myform.save()
        if myform.paid_value and myform.paid_value > 0:
            seller_pay = SellerPayments()
            seller_pay.seller = myform.seller
            seller_pay.paid_value = myform.paid_value
            seller_pay.paid_reason = ' دفعة فاتورة ' + str(self.kwargs['pk'])
            seller_pay.paid_type = 1
            seller_pay.save()
        return redirect(self.get_success_url())


class InvoiceBack(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Invoice
    form_class = InvoiceBackForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'الغاء حفظ الفاتورة: ' + str(self.object)
        context['message'] = 'inv_back'
        context['action_url'] = reverse_lazy('Invoices:InvoiceBack', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        form.save()
        myform = Invoice.objects.get(id=self.kwargs['pk'])
        myform.saved = 0
        # myform.discount = 0.0
        myform.overall = 0.0
        myform.save()
        return redirect(self.get_success_url())

    def get_success_url(self, **kwargs):
        messages.success(self.request, "تم الغاء حفظ الفاتورة بنجاح", extra_tags="success")
        return reverse('Invoices:InvoiceDetail', kwargs={'pk': self.object.id})


class InvoiceDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Invoice
    form_class = InvoiceDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Invoices:InvoiceList', kwargs={'type': self.object.invoice_type})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف الفاتورة: ' + str(self.object)
        context['message'] = 'deletee'
        context['action_url'] = reverse_lazy('Invoices:InvoiceDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف الفاتورة " + str(self.object) + ' بنجاح ', extra_tags="danger")
        myform = Invoice.objects.get(id=self.kwargs['pk'])
        myform.deleted = 1
        myform.save()
        return redirect(self.get_success_url())


def AllInvoiceDelete(request):
    invs3 = Invoice.objects.filter(invoice_type=3)
    invs3.delete()
    messages.success(request, "تم حذف جميع فواتير القطاعي بنجاح", extra_tags="success")
    return redirect('Invoices:InvoiceList', type=3)


class InvoiceRestore(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Invoice
    form_class = InvoiceDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Invoices:InvoiceTrashList', kwargs={'type': self.object.invoice_type})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'استرجاع الفاتورة: ' + str(self.object)
        context['message'] = 'restoree'
        context['action_url'] = reverse_lazy('Invoices:InvoiceRestore', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم استرجاع الفاتورة " + str(self.object) + ' بنجاح ', extra_tags="dark")
        myform = Invoice.objects.get(id=self.kwargs['pk'])
        myform.deleted = 0
        myform.save()
        return redirect(self.get_success_url())


class InvoiceSuperDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Invoice
    form_class = InvoiceDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Invoices:InvoiceTrashList', kwargs={'type': self.object.invoice_type})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف الفاتورة : ' + str(self.object.id) + 'بشكل نهائي'
        context['message'] = 'super_deletee'
        context['action_url'] = reverse_lazy('Invoices:InvoiceSuperDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف الفاتورة " + str(self.object.id) + " نهائيا بنجاح ", extra_tags="success")
        my_form = Invoice.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect(self.get_success_url())


def InvoiceDetail(request, pk):
    invoice = get_object_or_404(Invoice, id=pk)
    # if invoice.saved == 0:
    #     invoice.old_value = SellerDebit(invoice.seller.id) * -1
    #     invoice.save()
    product = InvoiceItem.objects.filter(invoice=invoice).order_by('id')
    count_product = product.count()

    total = product.aggregate(total=Sum('total_price')).get('total')
    quantity1 = product.filter(unit=1).aggregate(quantity=Sum('quantity')).get('quantity')
    if quantity1:
        quantity1 = quantity1
    else:
        quantity1 = 0.0
    quantity2 = product.filter(unit=12).aggregate(quantity=Sum('quantity')).get('quantity')
    if quantity2:
        quantity2 = quantity2
    else:
        quantity2 = 0.0
    quantity = quantity1 + (quantity2 * 12)

    if total:
        invoice.total = total
        invoice.save()

    form = InvoiceProductsForm()
    products = []
    for prod in product:
        products.append(prod.item.id)

    form.fields['item'].queryset = Product.objects.filter(deleted=False).exclude(id__in=products).order_by('name')

    type_page = "list"
    page = "active"
    action_url = reverse_lazy('Invoices:AddProductInvoice', kwargs={'pk': invoice.id})

    # if int(invoice.invoice_type) == 1 or int(invoice.invoice_type) == 2:
    #     if invoice.seller.agreement:
    #         messages.warning(request, "اتفاق مسبق مع التاجر: " + str(invoice.seller.agreement), extra_tags="warning")
    context = {
        'invoice': invoice,
        'type': type_page,
        'page': page,
        'form': form,
        'action_url': action_url,
        'product': product,
        'count_product': count_product,
        'total': total,
        'qu': quantity,
        'date': datetime.now().date(),

    }
    return render(request, 'Invoices/invoice_detail.html', context)


def AddProductInvoice(request, pk):
    invoice = get_object_or_404(Invoice, id=pk)
    product = InvoiceItem.objects.filter(invoice=invoice).order_by('id')
    count_product = product.count()

    form = InvoiceProductsForm(request.POST or None)
    formm = InvoiceProductsForm()

    type_page = "list"
    page = "active"
    action_url = reverse_lazy('Invoices:AddProductInvoice', kwargs={'pk': invoice.id})

    context = {
        'invoice': invoice,
        'type': type_page,
        'page': page,
        'form': formm,
        'action_url': action_url,
        'product': product,
        'count_product': count_product
    }

    if form.is_valid():
        quantity = form.cleaned_data.get("quantity") * form.cleaned_data.get("unit")
        item = form.cleaned_data.get("item")
        trans = item.quantity

        # if trans >= quantity:
        obj = form.save(commit=False)
        obj.invoice = invoice
        obj.save()
        messages.success(request, " تم اضافة منتج الي الفاتورة بنجاح ", extra_tags="success")
        # else:
        #     messages.success(request, " لاتوجد كمية كافية من المنتج داخل المخزن ", extra_tags="danger")
        return redirect('Invoices:InvoiceDetail', pk=invoice.id)

    return render(request, 'Invoices/invoice_detail.html', context)


class InvoiceProductsUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = InvoiceItem
    form_class = InvoiceProductsFormUpdate
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل المنتج: ' + str(self.object.item)
        context['message'] = 'updatee'
        context['inv_update'] = 'update'
        context['action_url'] = reverse_lazy('Invoices:InvoiceProductsUpdate', kwargs={'pk': self.object.id, 'id': self.object.invoice.id})
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class=self.form_class)
        form.fields['item'].queryset = Product.objects.filter(id=self.object.item.id)
        return form

    def get_success_url(self, **kwargs):
        return reverse('Invoices:InvoiceDetail', kwargs={'pk': self.kwargs['id']})

    def form_valid(self, form):
        quantity = form.cleaned_data.get("quantity") * form.cleaned_data.get("unit")
        unit_price = form.cleaned_data.get("unit_price")
        item = form.cleaned_data.get("item")
        trans = item.quantity
        object_item = self.object.item

        # if trans >= quantity:
        prod = form.save(commit=False)
        prod.total_price = float(quantity) * float(unit_price)
        form.save()
        messages.success(self.request, " تم تعديل منتج " + str(object_item) + " بنجاح ", extra_tags="success")
        # else:
        #     messages.success(self.request, " لاتوجد كمية كافية من المنتج داخل المخزن ", extra_tags="danger")
        return redirect(self.get_success_url())


def get_item_price(request):
    e = request.GET.get('e')
    product = Product.objects.get(id=int(e))
    if product.price:
        price = product.price
    else:
        price = 0.0
    data = json.dumps({
        'product_price': float(price),
    })
    return HttpResponse(data, content_type='application/json')


class InvoiceProductsDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = InvoiceItem
    form_class = InvoiceProductsDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Invoices:InvoiceDetail', kwargs={'pk': self.kwargs['id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف المنتج: ' + str(self.object.item)
        context['message'] = 'super_delete'
        context['action_url'] = reverse_lazy('Invoices:InvoiceProductsDelete', kwargs={'pk': self.object.id, 'id': self.object.invoice.id})
        return context

    def form_valid(self, form):
        object_item = self.object.item
        messages.success(self.request, " تم حذف المنتج " + str(object_item) + " من الفاتورة بنجاح ", extra_tags="success")
        my_form = InvoiceItem.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect(self.get_success_url())


def PrintInvoice(request, id):
    date = datetime.now()
    invoice = Invoice.objects.get(id=id)
    invoice_items = InvoiceItem.objects.filter(invoice=invoice, deleted=0)
    shop_setting = SystemInformation.objects.all()
    if shop_setting.count() > 0:
        shop_setting = shop_setting.last()
    else:
        shop_setting = None

    product = InvoiceItem.objects.filter(invoice=invoice).order_by('id')
    count_product = product.count()

    quantity1 = product.filter(unit=1).aggregate(quantity=Sum('quantity')).get('quantity')
    if quantity1:
        quantity1 = quantity1
    else:
        quantity1 = 0.0
    quantity2 = product.filter(unit=12).aggregate(quantity=Sum('quantity')).get('quantity')
    if quantity2:
        quantity2 = quantity2
    else:
        quantity2 = 0.0
    quantity = quantity1 + (quantity2 * 12)

    context = {
        'date': date,
        'user': request.user.username,
        'invoice': invoice,
        'invoice_items': invoice_items,
        'shop_setting': shop_setting,
        'count_product': count_product,
        'quantity': quantity,
    }
    html_string = render_to_string('Invoices/print_main_invoice.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/main_invoice_pdf.css')], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    return response


# def InvoiceReturn(request):
#     invoices = Invoice.objects.filter(deleted=0, saved=1, close=1)
#     context = {
#         'invoices': invoices,
#     }
#     return render(request, 'Invoices/invoice_return.html', context)
#
#
# def InvoiceReturnProduct(request):
#     invoices = Invoice.objects.filter(deleted=0, saved=1, close=1)
#     invoice_id = int(request.POST.get('invoice_id'))
#     invoice = Invoice.objects.get(id=invoice_id)
#     product = InvoiceItem.objects.filter(invoice__id=invoice_id)
#     r_product = InvoiceItemDetails.objects.filter(invoice__id=invoice_id)
#
#     total = product.aggregate(total=Sum('total_price')).get('total')
#     quantity1 = product.filter(unit=1).aggregate(quantity=Sum('quantity')).get('quantity')
#     if quantity1:
#         quantity1 = quantity1
#     else:
#         quantity1 = 0.0
#     quantity2 = product.filter(unit=12).aggregate(quantity=Sum('quantity')).get('quantity')
#     if quantity2:
#         quantity2 = quantity2
#     else:
#         quantity2 = 0.0
#     quantity = quantity1 + (quantity2 * 12)
#
#     form = InvoiceItemProductsForm()
#     products = []
#     for prod in product:
#         products.append(prod.item.id)
#
#     r_products = []
#     for prod in r_product:
#         r_products.append(prod.item.id)
#     form.fields['item'].queryset = Product.objects.filter(deleted=False, id__in=products).exclude(id__in=r_products)
#     context = {
#         'invoices': invoices,
#         'product': product,
#         'r_product': r_product,
#         'invoice_id': invoice_id,
#         'invoice': invoice,
#         'count_product': product.count(),
#         'total': total,
#         'qu': quantity,
#         'form': form,
#     }
#     return render(request, 'Invoices/invoice_return.html', context)
#
#
# def get_item_return_price(request):
#     l = request.GET.get('l').split(',')
#     item = InvoiceItem.objects.get(invoice__id=int(l[1]), item__id=int(l[0]))
#     if item.unit_price:
#         price = item.unit_price
#     else:
#         price = 0.0
#
#     if item.quantity:
#         quantity = item.quantity
#     else:
#         quantity = 0.0
#
#     if item.unit:
#         unit = item.unit
#     else:
#         unit = 1
#
#     data = json.dumps({
#         'product_price': float(price),
#         'product_quantity': float(quantity),
#         'product_unit': float(unit),
#     })
#     return HttpResponse(data, content_type='application/json')
#
#
# def ReturnProductInvoice(request, pk):
#     invoice = get_object_or_404(Invoice, id=pk)
#     form = InvoiceItemProductsForm(request.POST or None)
#     formm = InvoiceItemProductsForm()
#
#     invoices = Invoice.objects.filter(deleted=0, saved=1, close=1)
#     invoice_id = int(invoice.id)
#     product = InvoiceItem.objects.filter(invoice__id=invoice_id)
#     r_product = InvoiceItemDetails.objects.filter(invoice__id=invoice_id)
#
#     total = product.aggregate(total=Sum('total_price')).get('total')
#     quantity1 = product.filter(unit=1).aggregate(quantity=Sum('quantity')).get('quantity')
#     if quantity1:
#         quantity1 = quantity1
#     else:
#         quantity1 = 0.0
#     quantity2 = product.filter(unit=12).aggregate(quantity=Sum('quantity')).get('quantity')
#     if quantity2:
#         quantity2 = quantity2
#     else:
#         quantity2 = 0.0
#     quantity = quantity1 + (quantity2 * 12)
#
#     products = []
#     for prod in product:
#         products.append(prod.item.id)
#
#     r_products = []
#     for prod in r_product:
#         r_products.append(prod.item.id)
#     formm.fields['item'].queryset = Product.objects.filter(deleted=False, id__in=products).exclude(id__in=r_products)
#     context = {
#         'invoices': invoices,
#         'product': product,
#         'r_product': r_product,
#         'invoice_id': invoice_id,
#         'invoice': invoice,
#         'count_product': product.count(),
#         'total': total,
#         'qu': quantity,
#         'form': formm,
#     }
#
#     if form.is_valid():
#         item = form.cleaned_data.get("item")
#         invoice_item = InvoiceItem.objects.get(invoice=invoice, item=item)
#         # invoice_return_item = InvoiceItemDetails.objects.get(invoice=invoice, item=item)
#         # trans = (invoice_item.quantity * invoice_item.unit) - (invoice_return_item.quantity * invoice_return_item.unit)
#         trans = invoice_item.quantity * invoice_item.unit
#         quantity = form.cleaned_data.get("quantity") * form.cleaned_data.get("unit")
#
#         if trans >= quantity:
#             obj = form.save(commit=False)
#             obj.invoice = invoice
#             obj.invoice_item = invoice_item
#             obj.save()
#             messages.success(request, " تم ارجاع كمية منتج من الفاتورة بنجاح ", extra_tags="success")
#         else:
#             messages.success(request, " لاتوجد كمية كافية من المنتج داخل الفاتورة المختارة ", extra_tags="danger")
#         return render(request, 'Invoices/invoice_return.html', context)
#
#     return render(request, 'Invoices/invoice_return.html', context)