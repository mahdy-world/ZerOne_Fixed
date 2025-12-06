from audioop import reverse
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import *
from django.contrib import messages
from Core.forms import ColorForm, ExpensessTypeCreateForm, SystemInfoForm, ExpensessForm
from Core.models import SystemInformation
from Products.models import *
from Factories.models import Factory, Supplier
from Treasury.models import Treasury, TreasuryOperation
from Wool.models import Wool, WoolSupplier
from Workers.models import Worker
from Invoices.models import Invoice, InvoiceItem
from Core.models import *

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
# Create your views here.


@login_required(login_url='Auth:login')
def Index(request):
    modules = Modules.objects.all().last()
    today = datetime.now().date()
    return render(request, 'core/index.html', {'modules':modules, 'today': today})

class ExpensessTypeList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = ExpnsessType
    paginate_by = 12
    template_name = 'Core/expensses_type_list.html'
    
    def get_queryset(self):
        qureyset = self.model.objects.all().order_by('-id')
        return qureyset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'list'
        context['title'] = 'قائمة البنود'
        context['icons'] = '<i class="fas fa-shapes"></i>'
        context['page'] = 'active'
        context['count'] = self.model.objects.all().count()
        return context
    
class ExpensessTypeCreate(LoginRequiredMixin, CreateView):
    login_url = ' /auth/login/'
    model = ExpnsessType
    template_name = 'forms/form_template.html'
    form_class = ExpensessTypeCreateForm
    success_url = reverse_lazy('Core:ExpensessTypeList')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'اضافة نوع جديد'
        context['message'] = 'info'
        context['action_url'] = reverse_lazy('Core:ExpensessTypeCreate')
        return context
    
    def get_success_url(self):
        messages.success(self.request, "تم إضافة بند جديد  ", extra_tags="success")

        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url


class ExpensessTypeDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = ExpnsessType
    form_class = ExpensessTypeCreateForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف البند : ' + str(self.object.name)
        context['message'] = 'super_delete'
        context['action_url'] = reverse_lazy('Core:ExpensessTypeDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف البند " +  " نهائيا بنجاح ", extra_tags="success")
        my_form = ExpnsessType.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect('Core:ExpensessTypeList')


class ColorList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Color
    paginate_by = 12
    template_name = 'Core/color_list.html'
    
    def get_queryset(self):
        qureyset = self.model.objects.all().order_by('-id')
        return qureyset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'list'
        context['title'] = 'قائمة الالوان'
        context['icons'] = '<i class="fas fa-shapes"></i>'
        context['page'] = 'active'
        context['count'] = self.model.objects.all().count()
        return context
    
class ColorCreate(LoginRequiredMixin, CreateView):
    login_url = ' /auth/login/'
    model = Color
    template_name = 'forms/form_template.html'
    form_class = ColorForm
    success_url = reverse_lazy('Core:ColorList')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'اضافة لون في النظام'
        context['message'] = 'info'
        context['action_url'] = reverse_lazy('Core:ColorCreate')
        return context
    
    def get_success_url(self):
        messages.success(self.request, "تم إضافة بيانات للنظام بنجاح", extra_tags="success")

        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url
        
        
class ColorUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Color
    form_class = ColorForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل اللون: ' + str(self.object)
        context['message'] = 'update'
        context['action_url'] = reverse_lazy('Core:ColorUpdate', kwargs={'pk': self.object.id})
        return context
    
    def get_success_url(self):
        messages.success(self.request,  "تم تعديل اللون " + str(self.object) + " بنجاح ", extra_tags="success")
        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url
    

class ColorDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Color
    form_class = ColorForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف اللون : ' + str(self.object.color_name)
        context['message'] = 'super_delete'
        context['action_url'] = reverse_lazy('Core:ColorDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف اللون " + str(self.object) + " نهائيا بنجاح ", extra_tags="success")
        my_form = Color.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect('Core:ColorList')
    
        
class SystemInfoCreate(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = SystemInformation
    template_name = 'forms/form_template.html'
    form_class = SystemInfoForm
    success_url = reverse_lazy('Core:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'بيانات النظام'
        context['message'] = 'info'
        context['action_url'] = reverse_lazy('Core:SystemInfoCreate')
        return context
    
        # return reverse('Core:index')
        
    def form_valid(self, form):
        form.save()
        obj = form.save(commit=False)
        info = SystemInformation.objects.get(id=obj.id)

        logo = info.logo
        if logo:
            # Read the binary data of the image file
            image_data = logo.read()
            # Open the image using PIL
            img = Image.open(BytesIO(image_data))
            # Check if the image format is not PNG
            if img.format != 'PNG':
                # Convert the image to PNG
                img = img.convert('RGBA')
                png_data = BytesIO()
                img.save(png_data, format='PNG')
                png_file = SimpleUploadedFile("logo.png", png_data.getvalue(), content_type="image/png")
                # Save the converted PNG image back to the model
                info.logo = png_file
                info.save()

        return redirect(self.get_success_url())
    
    
class SystemInfoUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = SystemInformation
    template_name = 'forms/form_template.html'
    form_class = SystemInfoForm
    success_url = reverse_lazy('Core:index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل بيانات النظام'
        context['message'] = 'info'
        context['info_obj'] = self.object
        context['action_url'] = reverse_lazy('Core:SystemInfoUpdate',kwargs={'pk': self.object.id})
        return context
    
    def get_success_url(self):
        messages.success(self.request, " تم تعديل بيانات النظام بنجاح", extra_tags="success")

        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url
        # return reverse('Core:index')

    def form_valid(self, form):
        form.save()
        obj = form.save(commit=False)
        info = SystemInformation.objects.get(id=obj.id)

        logo = info.logo
        if logo:
            # Read the binary data of the image file
            image_data = logo.read()
            # Open the image using PIL
            img = Image.open(BytesIO(image_data))
            # Check if the image format is not PNG
            if img.format != 'PNG':
                # Convert the image to PNG
                img = img.convert('RGBA')
                png_data = BytesIO()
                img.save(png_data, format='PNG')
                png_file = SimpleUploadedFile("logo.png", png_data.getvalue(), content_type="image/png")
                # Save the converted PNG image back to the model
                info.logo = png_file
                info.save()

        return redirect(self.get_success_url())


class FactorySearch(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Factory
    template_name = 'Factory/factory_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['page'] = 'active'
        context['search'] = self.request.GET.get("factory")
        context['type'] = 'list'
        context['count'] = self.model.objects.filter(deleted=False).count()
        return context
    
    def get_queryset(self):
        search = self.request.GET.get("factory")  
        queryset = self.model.objects.filter(name__icontains=search, deleted=False)
        return queryset
    
    
class ProductSearch(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Product
    template_name = 'Products/product_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['page'] = 'active'
        context['product_serach'] = self.request.GET.get("product")
        context['type'] = 'list'
        context['count'] = self.model.objects.filter(deleted=False).count()
        return context
    
    def get_queryset(self):
        product_serach = self.request.GET.get("product")  
        queryset = self.model.objects.filter(name__icontains=product_serach, deleted=False)
        return queryset
    
class ProductSearch_size(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Product
    template_name = 'Products/product_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['page'] = 'active'
        context['product_serach_size'] = self.request.GET.get("product_size")
        context['type'] = 'list'
        context['count'] = self.model.objects.filter(deleted=False).count()
        return context
    
    def get_queryset(self):
        product_serach = self.request.GET.get("product_size")  
        queryset = self.model.objects.filter(size=int(product_serach), deleted=False)
        return queryset


class InvoiceSearch(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Invoice
    template_name = 'Invoices/invoice_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        if self.model.objects.filter(id=int(self.request.GET.get("invoice")), deleted=False):
            inv_type = self.model.objects.get(id=int(self.request.GET.get("invoice")), deleted=False).invoice_type
            context['type'] = inv_type
            context['count'] = self.model.objects.filter(deleted=False, invoice_type=inv_type).count()
        else:
            context['type'] = 1
            context['count'] = self.model.objects.filter(deleted=False, invoice_type=1).count()
        context['invoice_serach'] = self.request.GET.get("invoice")
        return context

    def get_queryset(self):
        invoice_serach = self.request.GET.get("invoice")
        queryset = self.model.objects.filter(id=int(invoice_serach), deleted=False)
        if queryset:
            inv_type = self.model.objects.get(id=int(invoice_serach), deleted=False).invoice_type
            queryset = queryset.filter(invoice_type=inv_type)
        else:
            queryset = self.model.objects.filter(deleted=False, invoice_type=1)
        return queryset


class SpInvoiceSearch(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Invoice
    template_name = 'Invoices/invoice_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['type'] = self.kwargs['type']
        context['invoice_serach'] = self.request.GET.get("invoice")
        context['count'] = self.model.objects.filter(deleted=False, invoice_type=int(self.kwargs['type'])).count()
        return context

    def get_queryset(self):
        invoice_serach = self.request.GET.get("invoice")
        queryset = self.model.objects.filter(id=int(invoice_serach), deleted=False, invoice_type=int(self.kwargs['type']))
        if queryset:
            queryset = queryset
        else:
            queryset = self.model.objects.filter(deleted=False, invoice_type=int(self.kwargs['type']))
        return queryset


class WorkerSearch(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Worker
    template_name = 'Worker/worker_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['page'] = 'active'
        context['worker_serach'] = self.request.GET.get("worker")
        context['type'] = 'list'
        context['count'] = self.model.objects.filter(deleted=False).count()
        return context
    
    def get_queryset(self):
        worker_serach = self.request.GET.get("worker")  
        queryset = self.model.objects.filter(name__icontains=worker_serach, deleted=False)
        return queryset


class SellerSearch(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = ProductSellers
    paginate_by = 6

    def get_queryset(self):
        seller = self.request.GET.get('seller')
        queryset = self.model.objects.filter(deleted=False, name__icontains=str(seller)).order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'list'
        context['title'] = 'قائمة التجار'
        context['seller_serach'] = self.request.GET.get('seller')
        context['page'] = 'active'
        context['seller_search'] = self.request.GET.get('seller')
        context['count'] = self.model.objects.filter(deleted=False).count()
        return context


class SpSupplierSearch(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Supplier
    template_name = 'Supplier/supplier_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['type'] = self.kwargs['type']
        context['search'] = self.request.GET.get("supplier")
        context['count'] = self.model.objects.filter(deleted=False, type=int(self.kwargs['type'])).count()
        return context

    def get_queryset(self):
        search = self.request.GET.get("supplier")
        queryset = self.model.objects.filter(name=search, deleted=False, type=int(self.kwargs['type']))
        if queryset:
            queryset = queryset
        else:
            queryset = self.model.objects.filter(deleted=False, type=int(self.kwargs['type']))
        return queryset


class SellerInvoiceSearch(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Invoice
    template_name = 'Invoices/invoice_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['type'] = self.kwargs['type']
        context['seller_invoice_search'] = self.request.GET.get("seller_invoice")
        context['count'] = self.model.objects.filter(deleted=False, invoice_type=int(self.kwargs['type'])).count()
        return context

    def get_queryset(self):
        seller_invoice_search = self.request.GET.get("seller_invoice")
        queryset = self.model.objects.filter(seller__name__icontains=seller_invoice_search, deleted=False, invoice_type=int(self.kwargs['type']))
        if queryset:
            queryset = queryset
        else:
            messages.error(self.request, "خطأ! لايوجد فواتير لهذا التاجر ", extra_tags="danger")
            queryset = self.model.objects.filter(deleted=False, invoice_type=int(self.kwargs['type']))
        return queryset


class ClientInvoiceSearch(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Invoice
    template_name = 'Invoices/invoice_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['type'] = self.kwargs['type']
        context['client_invoice_search'] = self.request.GET.get("client_invoice")
        context['count'] = self.model.objects.filter(deleted=False, invoice_type=int(self.kwargs['type'])).count()
        return context

    def get_queryset(self):
        client_invoice_search = self.request.GET.get("client_invoice")
        queryset = self.model.objects.filter(customer__icontains=client_invoice_search, deleted=False, invoice_type=int(self.kwargs['type']))
        if queryset:
            queryset = queryset
        else:
            messages.error(self.request, "خطأ! لايوجد فواتير لهذا العميل ", extra_tags="danger")
            queryset = self.model.objects.filter(deleted=False, invoice_type=int(self.kwargs['type']))
        return queryset
    

class TreasurySearch(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Treasury
    template_name = 'Treasury/treasury_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['page'] = 'active'
        context['treasury_serach_val'] = self.request.GET.get("treasury")
        context['type'] = 'list'
        context['count'] = self.model.objects.filter(deleted=False).count()
        return context
    
    def get_queryset(self):
        treasury_serach = self.request.GET.get("treasury")  
        queryset = self.model.objects.filter(name__icontains=treasury_serach, deleted=False)
        return queryset


class WoolSupplierSearch(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = WoolSupplier
    template_name = 'WoolSupplier/supplier_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['wool_supplier_search'] = self.request.GET.get("wool_supplier")
        context['count'] = self.model.objects.filter(deleted=False).count()
        return context

    def get_queryset(self):
        search = self.request.GET.get("wool_supplier")
        queryset = self.model.objects.filter(name=search, deleted=False)
        
        return queryset
    
class WoolSearch(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Wool
    template_name = 'Wool/wool_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['wool_search'] = self.request.GET.get("wool")
        context['count'] = Wool.objects.all().count()
        return context

    def get_queryset(self):
        search = self.request.GET.get("wool")
        queryset = self.model.objects.filter(wool_name=search)
        if queryset:
            queryset = queryset
        else:
            queryset = Wool.objects.all()
        return queryset


def SystemStatistics(request):
    st_time = request.POST.get('st_time')
    if not st_time:
        st_time = 'today'

    fltr = {}
    fltrr = {}
    fltrrr = {}

    if st_time == 'today':
        d = datetime.now().date()
        fltr['date'] = d
        fltrr['date__date'] = d
        fltrrr['operation_date__date'] = d

    if st_time == 'yesterday':
        d = datetime.now() - timedelta(days=1)
        d = d.strftime('%Y-%m-%d')
        fltr['date__gte'] = d
        fltrr['date__date__gte'] = d
        fltrrr['operation_date__date__gte'] = d

    if st_time == '3days':
        d = datetime.now() - timedelta(days=3)
        d = d.strftime('%Y-%m-%d')
        fltr['date__gt'] = d
        fltrr['date__date__gt'] = d
        fltrrr['operation_date__date__gt'] = d

    if st_time == '1week':
        d = datetime.now() - timedelta(weeks=1)
        d = d.strftime('%Y-%m-%d')
        fltr['date__gt'] = d
        fltrr['date__date__gt'] = d
        fltrrr['operation_date__date__gt'] = d

    if st_time == '1month':
        d = datetime.now() - relativedelta(months=1)
        d = d.strftime('%Y-%m-%d')
        fltr['date__gt'] = d
        fltrr['date__date__gt'] = d
        fltrrr['operation_date__date__gt'] = d

    if st_time == '3months':
        d = datetime.now() - relativedelta(months=3)
        d = d.strftime('%Y-%m-%d')
        fltr['date__gt'] = d
        fltrr['date__date__gt'] = d
        fltrrr['operation_date__date__gt'] = d

    if st_time == '6months':
        d = datetime.now() - relativedelta(months=6)
        d = d.strftime('%Y-%m-%d')
        fltr['date__gt'] = d
        fltrr['date__date__gt'] = d
        fltrrr['operation_date__date__gt'] = d

    if st_time == '1year':
        d = datetime.now() - relativedelta(years=1)
        d = d.strftime('%Y-%m-%d')
        fltr['date__gt'] = d
        fltrr['date__date__gt'] = d
        fltrrr['operation_date__date__gt'] = d

    inv1 = Invoice.objects.filter(invoice_type=1, close=True, **fltr)
    inv1_items = InvoiceItem.objects.filter(invoice__in=inv1)
    money_in = SellerPayments.objects.filter(paid_type=1, **fltrr)
    inv1_dict = {
        'invs': inv1.count(),
        'quants': inv1_items.aggregate(sum=Sum('quantity')).get('sum'),
        'total': inv1.aggregate(sum=Sum(F('total') - F('discount'))).get('sum'),
        'collects': money_in.aggregate(sum=Sum('paid_value')).get('sum'),
    }

    inv2 = Invoice.objects.filter(invoice_type=2, close=True, **fltr)
    inv2_items = InvoiceItem.objects.filter(invoice__in=inv2)
    money_out = SellerPayments.objects.filter(paid_type=2, **fltrr)
    inv2_dict = {
        'invs': inv2.count(),
        'quants': inv2_items.aggregate(sum=Sum('quantity')).get('sum'),
        'total': inv2.aggregate(sum=Sum(F('total') - F('discount'))).get('sum'),
        'collects': money_out.aggregate(sum=Sum('paid_value')).get('sum'),
    }

    inv3 = Invoice.objects.filter(invoice_type=3, close=True, **fltr)
    inv3_items = InvoiceItem.objects.filter(invoice__in=inv3)
    inv3_dict = {
        'invs': inv3.count(),
        'quants': inv3_items.aggregate(sum=Sum('quantity')).get('sum'),
        'total': inv3.aggregate(sum=Sum(F('total') - F('discount'))).get('sum'),
    }

    treasuries_in = TreasuryOperation.objects.filter(treasury__deleted=0, operation_type=1, **fltrrr)
    treasuries_out = TreasuryOperation.objects.filter(treasury__deleted=0, operation_type=2, **fltrrr)
    if treasuries_in:
        treasuries_in = treasuries_in.aggregate(sum=Sum('operation_value')).get('sum')
    else:
        treasuries_in = 0
    if treasuries_out:
        treasuries_out = treasuries_out.aggregate(sum=Sum('operation_value')).get('sum')
    else:
        treasuries_out = 0

    treasuries_balance = Treasury.objects.filter(deleted=0)
    if treasuries_balance:
        treasuries_balance = treasuries_balance.aggregate(sum=Sum('balance')).get('sum')
    else:
        treasuries_balance = 0
    treasuries_dict = {
        'treasuries_in': treasuries_in,
        'treasuries_out': treasuries_out,
        'treasuries_balance': treasuries_balance,
    }

    return render(request, 'components/statistics.html', {
        'st_time': st_time,
        'inv1_dict': inv1_dict,
        'inv2_dict': inv2_dict,
        'inv3_dict': inv3_dict,
        'treasuries_dict': treasuries_dict,
    })


def ExpensessDetail(request):

    form = ExpensessForm()
    expensess_type = ExpnsessType.objects.all()
    object_list = Expnsess.objects.all().order_by('-id')
    action_url = reverse_lazy('Core:ExpensessCreate')
    system_info = SystemInformation.objects.all()
    if system_info.count() > 0:
        system_info = system_info.last()
    else:
        system_info = None

    context = {
        'form': form,
        'action_url': action_url,
        'system_info': system_info,
        'date': datetime.now().date(),
        'expensess_type': expensess_type,
        'object_list': object_list
    }
    return render(request, 'Core/expensses_list.html', context)


def ExpensessCreate(request):
    express_type = ExpnsessType.objects.get(id=request.POST.get('expnsess_type'))
    form = ExpensessForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.admin = request.user 
        obj.expnsess_type= express_type
        obj.save()
        messages.success(request, " تم اضافة مصروف جديد ", extra_tags="success")
    else:
        messages.error(request, " حدث خطأ أثناء اضافة المصروف ", extra_tags="danger")
    return redirect('Core:ExpensessDetail')


class ExpensessDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Expnsess
    form_class = ExpensessForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف البند : '
        context['message'] = 'super_delete'
        context['action_url'] = reverse_lazy('Core:ExpensessDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف البند " +  " نهائيا بنجاح ", extra_tags="success")
        my_form = Expnsess.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect('Core:ExpensessDetail')