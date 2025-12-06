import datetime
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import *
from Core.models import SystemInformation
from .forms import *
from django.contrib import messages
import weasyprint
from django.template.loader import render_to_string
from Invoices.models import *
from Factories.models import *
from django.db.models import F
import base64
import os
from django.conf import settings
# Create your views here.


class ProductList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Product
    paginate_by = 12

    def get_queryset(self):
        queryset = self.model.objects.filter(deleted=False).order_by('-id')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'list'
        context['title'] = 'قائمة '
        context['page'] = 'active'
        context['count'] = self.model.objects.filter(deleted=False).count()
        return context
    

class ProductTrachList(LoginRequiredMixin, ListView):
    login_url = '/auth/login'
    model = Product
    paginate_by = 12
    
    def get_queryset(self):
        queryset = self.model.objects.filter(deleted=True).order_by('-id')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'trach'
        context['count'] = self.model.objects.filter(deleted=True).count()
        return context


class ProductCreate(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = Product
    form_class = ProductForm
    template_name = 'forms/product_form.html'
    success_url = reverse_lazy('Products:ProductList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'اضافة منتج جديد'
        context['message'] = 'add'
        context['action_url'] = reverse_lazy('Products:ProductCreate')
        return context
    
    def get_success_url(self):
        messages.success(self.request, "تم اضافة منتج جديد", extra_tags="success")

        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url


class ProductUpdate(LoginRequiredMixin ,UpdateView):
    login_url = '/auth/login/'
    model = Product
    form_class = ProductFormUpdate
    template_name = 'forms/product_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل المنتج: ' + str(self.object)
        context['message'] = 'update'
        context['action_url'] = reverse_lazy('Products:ProductUpdate', kwargs={'pk': self.object.id})
        return context
    
    def get_success_url(self):
        messages.success(self.request,  "تم تعديل المنتج " + str(self.object) + " بنجاح ", extra_tags="success")
        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url            


class AddProductQuantity(LoginRequiredMixin ,UpdateView):
    login_url = '/auth/login/'
    model = Product
    form_class = ProductQuantityForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'اضافة كمية للمنتج: ' + str(self.object)
        context['message'] = 'add'
        context['action_url'] = reverse_lazy('Products:AddProductQuantity', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        myform = Product.objects.get(id=self.kwargs['pk'])
        myform.quantity += int(form.cleaned_data.get("add_quant"))
        myform.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request,  "تم اضافة كمية للمنتج " + str(self.object) + " بنجاح ", extra_tags="success")
        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url


class MinusProductQuantity(LoginRequiredMixin ,UpdateView):
    login_url = '/auth/login/'
    model = Product
    form_class = ProductQuantityMinusForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'خصم كمية من المنتج: ' + str(self.object)
        context['message'] = 'add'
        context['action_url'] = reverse_lazy('Products:MinusProductQuantity', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        myform = Product.objects.get(id=self.kwargs['pk'])
        if myform.quantity >= int(form.cleaned_data.get("add_quant")):
            myform.quantity -= int(form.cleaned_data.get("add_quant"))
            myform.save()
            messages.success(self.request, "تم خصم كمية من المنتج " + str(self.object) + " بنجاح ",
                             extra_tags="success")
        else:
            messages.error(self.request, "خطأ! لم يتم خصم الكمية من المنتج " + str(self.object) + " تأكد من توفر الكمية ",
                             extra_tags="danger")

        return redirect(self.get_success_url())

    def get_success_url(self):
        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url


class ProductDelete(LoginRequiredMixin ,UpdateView):
    login_url = '/auth/login/'
    model = Product
    form_class = ProductDeleteForm
    template_name = 'forms/product_form.html'
    

    def get_success_url(self):
        return reverse('Products:ProductList')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'نقل المنتج الي سلة المهملات: ' + str(self.object)
        context['message'] = 'delete'
        context['action_url'] = reverse_lazy('Products:ProductDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم نقل المنتج " + str(self.object) + ' الي سلة المهملات بنجاح ' , extra_tags="success")
        myform = Product.objects.get(id=self.kwargs['pk'])
        myform.deleted = 1
        myform.save()
        return redirect(self.get_success_url())                


class ProductRestore(LoginRequiredMixin ,UpdateView):
    login_url = '/auth/login/'
    model = Product
    form_class = ProductDeleteForm
    template_name = 'forms/product_form.html'
    

    def get_success_url(self):
        return reverse('Products:ProductList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'استرجاع منتج: ' + str(self.object)
        context['message'] = 'restore'
        context['action_url'] = reverse_lazy('Products:ProductRestore', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم استرجاع المنتج " + str(self.object) + ' الي القائمة بنجاح ' , extra_tags="success")
        myform = Product.objects.get(id=self.kwargs['pk'])
        myform.deleted = 0
        myform.save()
        return redirect(self.get_success_url())
    

class ProductSuperDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Product
    form_class = ProductDeleteForm
    template_name = 'forms/product_form.html'

    def get_success_url(self):
        return reverse('Products:ProductTrachList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف المنتج: ' + str(self.object)
        context['message'] = 'super_delete'
        context['action_url'] = reverse_lazy('Products:ProductSuperDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف المنتج " + str(self.object) + " نهائيا بنجاح ", extra_tags="success")
        my_form = Product.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect(self.get_success_url())


class ProductDetails(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Invoice
    template_name = 'Products/product_detail.html'

    def get_context_data(self, **kwargs):
        product = Product.objects.get(id=int(self.kwargs['pk']))
        context = super().get_context_data(**kwargs)
        context['title'] = 'إنتاج ومبيعات الموديل: ' + str(product.name)
        context['type'] = 'list'
        context['factory_in'] = FactoryInSide.objects.filter(product=product).order_by('-date', '-id')
        context['factory_in_sum'] = FactoryInSide.objects.filter(product=product).order_by('-date', '-id').aggregate(sum=Sum('product_count')).get('sum')

        context['invoices'] = InvoiceItem.objects.filter(item=product, invoice__invoice_type__in=[1, 3], invoice__saved=True).order_by('-date', '-id')
        context['invoices_sum'] = InvoiceItem.objects.filter(item=product, invoice__invoice_type__in=[1, 3], invoice__saved=True).order_by('-date', '-id').aggregate(sum=Sum(F('quantity') * F('unit'))).get('sum')
        context['r_invoices'] = InvoiceItem.objects.filter(item=product, invoice__invoice_type=2, invoice__saved=True).order_by('-date', '-id')
        context['r_invoices_sum'] = InvoiceItem.objects.filter(item=product, invoice__invoice_type=2, invoice__saved=True).order_by('-date', '-id').aggregate(sum=Sum(F('quantity') * F('unit'))).get('sum')

        context['supplier'] = SupplierQuantity.objects.filter(product=product, supplier__type=1).order_by('-date', '-id')
        context['supplier_sum'] = SupplierQuantity.objects.filter(product=product, supplier__type=1).order_by('-date', '-id').aggregate(sum=Sum('product_count')).get('sum')
        context['importer'] = SupplierQuantity.objects.filter(product=product, supplier__type=2).order_by('-date', '-id')
        context['importer_sum'] = SupplierQuantity.objects.filter(product=product, supplier__type=2).order_by('-date', '-id').aggregate(sum=Sum('product_count')).get('sum')

        if context['factory_in_sum']:
            context['factory_in_sum'] = context['factory_in_sum']
        else:
            context['factory_in_sum'] = 0

        if context['invoices_sum']:
            context['invoices_sum'] = context['invoices_sum']
        else:
            context['invoices_sum'] = 0

        if context['r_invoices_sum']:
            context['r_invoices_sum'] = context['r_invoices_sum']
        else:
            context['r_invoices_sum'] = 0

        if context['supplier_sum']:
            context['supplier_sum'] = context['supplier_sum']
        else:
            context['supplier_sum'] = 0

        if context['importer_sum']:
            context['importer_sum'] = context['importer_sum']
        else:
            context['importer_sum'] = 0

        if product.quantity:
            product_quantity = product.quantity
        else:
            product_quantity = 0

        context['total'] = context['factory_in_sum'] + product_quantity - (context['invoices_sum'] - context['r_invoices_sum']) - (context['importer_sum'] - context['supplier_sum'])

        context['product'] = product
        return context


###################################################################


class SellerList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = ProductSellers
    paginate_by = 12

    def get_queryset(self):
        qureyset = self.model.objects.filter(deleted=False).order_by('-id')
        return qureyset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'list'
        context['title'] = 'قائمة التجار'
        context['page'] = 'active'
        context['count'] = self.model.objects.filter(deleted=False).count()
        return context


class SellerTrashList(LoginRequiredMixin, ListView):
    login_url = '/auth/login'
    model = ProductSellers
    paginate_by = 12

    def get_queryset(self):
        queyset = self.model.objects.filter(deleted=True).order_by('-id')
        return queyset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'trach'
        context['count'] = self.model.objects.filter(deleted=True).count()
        return context


class SellerCreate(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = ProductSellers
    form_class = ProductSellerForm
    template_name = 'forms/seller_product_form.html'
    success_url = reverse_lazy('Products:SellerList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'اضافة تاجر جديد'
        context['message'] = 'add'
        context['action_url'] = reverse_lazy('Products:SellerCreate')
        return context

    def get_success_url(self):
        messages.success(self.request, "تم اضافة تاجر جديد", extra_tags="success")

        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url


class SellerUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = ProductSellers
    form_class = ProductSellerFormUpdate
    template_name = 'forms/seller_product_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل التاجر: ' + str(self.object)
        context['message'] = 'update'
        context['action_url'] = reverse_lazy('Products:SellerUpdate', kwargs={'pk': self.object.id})
        return context

    def get_success_url(self):
        messages.success(self.request, "تم تعديل التاجر " + str(self.object) + " بنجاح ", extra_tags="success")
        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url


class PaidSellerValue(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = SellerPayments
    form_class = ProductSellerPaymentForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'استلام مبلغ من التاجر: ' + str(ProductSellers.objects.get(id=self.kwargs['pk']).name)
        context['message'] = 'add'
        context['action_url'] = reverse_lazy('Products:PaidSellerValue', kwargs={'pk': self.kwargs['pk']})
        return context

    def form_valid(self, form):
        seller = ProductSellers.objects.get(id=self.kwargs['pk'])
        myform = SellerPayments()
        myform.seller = seller
        myform.paid_value = form.cleaned_data.get("paid_value")
        myform.paid_reason = form.cleaned_data.get("paid_reason")
        myform.date = form.cleaned_data.get("date")
        myform.paid_type = 1
        myform.op = True
        myform.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, "تم استلام مبلغ من التاجر " + str(ProductSellers.objects.get(id=self.kwargs['pk']).name) + " بنجاح ", extra_tags="success")
        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url


class PaidSellerValue2(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = SellerPayments
    form_class = ProductSellerPaymentForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تسليم مبلغ الي التاجر: ' + str(ProductSellers.objects.get(id=self.kwargs['pk']).name)
        context['message'] = 'add'
        context['action_url'] = reverse_lazy('Products:PaidSellerValue2', kwargs={'pk': self.kwargs['pk']})
        return context

    def form_valid(self, form):
        seller = ProductSellers.objects.get(id=self.kwargs['pk'])
        myform = SellerPayments()
        myform.seller = seller
        myform.paid_value = form.cleaned_data.get("paid_value")
        myform.paid_reason = form.cleaned_data.get("paid_reason")
        myform.date = form.cleaned_data.get("date")
        myform.paid_type = 2
        myform.op = True
        myform.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, "تم تسليم مبلغ الي التاجر " + str(ProductSellers.objects.get(id=self.kwargs['pk']).name) + " بنجاح ", extra_tags="success")
        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url


class SellerDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = ProductSellers
    form_class = ProductSellerDeleteForm
    template_name = 'forms/seller_product_form.html'

    def get_success_url(self):
        return reverse('Products:SellerList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'نقل التاجر الي سلة المهملات: ' + str(self.object)
        context['message'] = 'delete'
        context['action_url'] = reverse_lazy('Products:SellerDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم نقل التاجر " + str(self.object) + ' الي سلة المهملات بنجاح ', extra_tags="success")
        myform = ProductSellers.objects.get(id=self.kwargs['pk'])
        myform.deleted = 1
        myform.save()
        return redirect(self.get_success_url())


class SellerRestore(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = ProductSellers
    form_class = ProductSellerDeleteForm
    template_name = 'forms/seller_product_form.html'

    def get_success_url(self):
        return reverse('Products:SellerList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'استرجاع تاجر: ' + str(self.object)
        context['message'] = 'restore'
        context['action_url'] = reverse_lazy('Products:SellerRestore', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم استرجاع التاجر " + str(self.object) + ' الي القائمة بنجاح ', extra_tags="success")
        myform = ProductSellers.objects.get(id=self.kwargs['pk'])
        myform.deleted = 0
        myform.save()
        return redirect(self.get_success_url())


class SellerSuperDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = ProductSellers
    form_class = ProductSellerDeleteForm
    template_name = 'forms/seller_product_form.html'

    def get_success_url(self):
        return reverse('Products:SellerTrashList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف التاجر: ' + str(self.object)
        context['message'] = 'super_delete'
        context['seller_del'] = True
        context['action_url'] = reverse_lazy('Products:SellerSuperDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف التاجر " + str(self.object) + " نهائيا بنجاح ", extra_tags="success")
        my_form = ProductSellers.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect(self.get_success_url())


class SellerDetails(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = SellerPayments
    template_name = 'Products/productsellers_detail.html'
    # paginate_by = 5

    def get_queryset(self):
        queryset = SellerPayments.objects.filter(seller=self.kwargs['pk'], paid_value__gt=0).order_by('-date', '-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'عمليات استلام/تسليم مبالغ من/الي التاجر: ' + str(ProductSellers.objects.get(id=self.kwargs['pk']).name)
        context['type'] = 'list'
        seller = ProductSellers.objects.get(id=int(self.kwargs['pk']))
        context['seller'] = seller
        context['from'] = SellerPayments.objects.filter(seller=seller, paid_value__gt=0, paid_type=1).aggregate(sum=Sum('paid_value'))
        context['to'] = SellerPayments.objects.filter(seller=seller, paid_value__gt=0, paid_type=2).aggregate(sum=Sum('paid_value'))
        context['count'] = SellerPayments.objects.filter(seller=seller, paid_value__gt=0).order_by('date', 'id').count()

        context['invoices'] = Invoice.objects.filter(seller=seller, invoice_type=1).order_by('-date', '-id')
        context['invoices_sum'] = Invoice.objects.filter(seller=seller, invoice_type=1).order_by('-date', '-id').aggregate(sum=Sum(F('total') - F('discount'))).get('sum')
        # context['invoices_r_sum'] = Invoice.objects.filter(seller=seller, invoice_type=1).order_by('-date', '-id').aggregate(sum=Sum('return_value')).get('sum')
        context['r_invoices'] = Invoice.objects.filter(seller=seller, invoice_type=2).order_by('-date', '-id')
        context['r_invoices_sum'] = Invoice.objects.filter(seller=seller, invoice_type=2).order_by('-date', '-id').aggregate(sum=Sum(F('total') - F('discount'))).get('sum')

        if context['invoices_sum']:
            context['invoices_sum'] = context['invoices_sum']
        else:
            context['invoices_sum'] = 0.0

        # if context['invoices_r_sum']:
        #     context['invoices_r_sum'] = context['invoices_r_sum']
        # else:
        #     context['invoices_r_sum'] = 0.0

        if context['r_invoices_sum']:
            context['r_invoices_sum'] = context['r_invoices_sum']
        else:
            context['r_invoices_sum'] = 0.0

        if SellerPayments.objects.filter(seller=seller, paid_value__gt=0):
            context['last_pay_id'] = SellerPayments.objects.filter(seller=seller, paid_value__gt=0).last().id
        else:
            context['last_pay_id'] = None

        return context


def SellerPaymentDelete(request, id):
    pay = SellerPayments.objects.get(id=id)
    pk = pay.seller.id
    pay.delete()
    messages.success(request, "تم حذف القيمة بنجاح", extra_tags="success")
    return redirect('Products:SellerDetails', pk=pk)


def PrintSellerInvoicesDetails(request, pk):
    # check0 = request.POST.get('check0')
    # check1 = request.POST.get('check1')
    # check2 = request.POST.get('check2')
    # check3 = request.POST.get('check3')
    # check4 = request.POST.get('check4')
    check0 = request.GET.get('check0')
    check1 = request.GET.get('check1')
    check2 = request.GET.get('check2')
    check3 = request.GET.get('check3')
    check4 = request.GET.get('check4')
    seller = ProductSellers.objects.get(id=pk)
    system_info = SystemInformation.objects.all()
    if system_info.count() > 0:
        system_info = system_info.last()
        # تحويل الصورة إلى base64
        if system_info.logo:
            logo_path = os.path.join(settings.MEDIA_ROOT, str(system_info.logo))
            try:
                with open(logo_path, 'rb') as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    system_info.logo_base64 = f"data:image/{logo_path.split('.')[-1]};base64,{encoded_string}"
            except:
                system_info.logo_base64 = None
        else:
            system_info.logo_base64 = None
    else:
        system_info = None

    if seller:
        initial_debit = seller.initial_balance_debit
    else:
        initial_debit = 0

    invoices = Invoice.objects.filter(seller=seller, invoice_type=1).order_by('-date', '-id')
    invoices_sum = invoices.aggregate(sum=Sum(F('total') - F('discount'))).get('sum')
    # invoices_r_sum = invoices.aggregate(sum=Sum('return_value')).get('sum')
    r_invoices = Invoice.objects.filter(seller=seller, invoice_type=2).order_by('-date', '-id')
    r_invoices_sum = r_invoices.aggregate(sum=Sum(F('total') - F('discount'))).get('sum')

    if invoices_sum:
        invoices_sum = invoices_sum
    else:
        invoices_sum = 0

    # if invoices_r_sum:
    #     invoices_r_sum = invoices_r_sum
    # else:
    #     invoices_r_sum = 0

    if r_invoices_sum:
        r_invoices_sum = r_invoices_sum
    else:
        r_invoices_sum = 0

    # invoices_overall = float(invoices_sum) - float(invoices_r_sum) - float(r_invoices_sum)
    invoices_overall = float(invoices_sum) - float(r_invoices_sum)

    seller_payments_from = SellerPayments.objects.filter(seller=seller, paid_type=1, paid_value__gt=0)
    payments_from = seller_payments_from.aggregate(sum=Sum('paid_value')).get('sum')
    seller_payments_to = SellerPayments.objects.filter(seller=seller, paid_type=2, paid_value__gt=0)
    payments_to = seller_payments_to.aggregate(sum=Sum('paid_value')).get('sum')

    if payments_from:
        payments_from = payments_from
    else:
        payments_from = 0

    if payments_to:
        payments_to = payments_to
    else:
        payments_to = 0

    payment_s = float(payments_from) - float(payments_to)

    # if seller.initial_balance_type == 1:
    #     payment_sum = (float(payments_from) - float(payments_to)) + float(initial_debit)
    # else:
    #     payment_sum = (float(payments_from) - float(payments_to)) - float(initial_debit)

    if seller.initial_balance_type == 1:
        payment_sum = (float(invoices_overall) - float(payments_from) + float(payments_to)) - float(initial_debit)
    else:
        payment_sum = (float(invoices_overall) - float(payments_from) + float(payments_to)) + float(initial_debit)

    invoices_items = InvoiceItem.objects.filter(invoice__seller=seller, invoice__invoice_type=1).order_by('-date', '-id')
    invoices_items_sum = invoices_items.aggregate(sum=Sum(F('quantity') * F('unit'))).get('sum')
    r_invoices_items = InvoiceItem.objects.filter(invoice__seller=seller, invoice__invoice_type=2).order_by('-date', '-id')
    r_invoices_items_sum = r_invoices_items.aggregate(sum=Sum(F('quantity') * F('unit'))).get('sum')

    if invoices_items_sum:
        invoices_items_sum = int(invoices_items_sum)
    else:
        invoices_items_sum = 0

    if r_invoices_items_sum:
        r_invoices_items_sum = int(r_invoices_items_sum)
    else:
        r_invoices_items_sum = 0

    all_invoices_items = invoices_items_sum - r_invoices_items_sum

    default_icon = os.path.join(settings.BASE_DIR, 'static', 'assets', 'images', 'new.png')

    context = {
        'system_info': system_info,
        'date': datetime.now(),
        'user': request.user.username,
        'seller': seller,
        'invoices': invoices,
        'invoices_sum': invoices_sum,
        'r_invoices': r_invoices,
        'r_invoices_sum': r_invoices_sum,
        'payment_sum': payment_sum,
        # 'invoices_r_sum': invoices_r_sum,
        'seller_payments_from': seller_payments_from,
        'seller_payments_to': seller_payments_to,
        'payments_from': payments_from,
        'payments_to': payments_to,
        'payment_s': payment_s,
        'invoices_overall': invoices_overall,
        'initial_debit': initial_debit,
        'invoices_items_sum': invoices_items_sum,
        'r_invoices_items_sum': r_invoices_items_sum,
        'all_invoices_items': all_invoices_items,
        'check0': check0,
        'check1': check1,
        'check2': check2,
        'check3': check3,
        'check4': check4,
        'default_icon': default_icon,
    }
    html_string = render_to_string('Products/print_seller_invoices_details.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    # pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/invoice_pdf.css')], presentational_hints=True)
    css_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'css', 'invoice_pdf.css')
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS(css_path)], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    # modal
    response['Content-Disposition'] = 'inline; filename="treasury_report.pdf"'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response