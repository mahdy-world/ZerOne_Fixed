import datetime
import json
from django.db.models.aggregates import Sum, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import *
from Core.models import SystemInformation
from .forms import *
from django.contrib import messages
import weasyprint
from django.template.loader import render_to_string
from datetime import datetime
import base64
import os
from django.conf import settings
# Create your views here.


class WoolSupplierList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = WoolSupplier
    paginate_by = 12
    template_name = 'WoolSupplier/supplier_list.html'

    def get_queryset(self):
        queryset = self.model.objects.filter(deleted=False).order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['count'] = self.model.objects.filter(deleted=False).count()
        return context


class WoolSupplierTrashList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = WoolSupplier
    paginate_by = 12
    template_name = 'WoolSupplier/supplier_list.html'

    def get_queryset(self):
        queryset = self.model.objects.filter(deleted=True).order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'trash'
        context['count'] = self.model.objects.filter(deleted=True).count()
        return context


class WoolSupplierCreate(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = WoolSupplier
    form_class = WoolSupplierForm
    template_name = 'forms/form_template.html'
    success_url = reverse_lazy('Wool:WoolSupplierList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'اضافة مورد خيط'
        context['message'] = 'create'
        context['action_url'] = reverse_lazy('Wool:WoolSupplierCreate')
        return context

    def get_success_url(self):
        messages.success(self.request, "تم اضافة مورد خيط جديد", extra_tags="success")
        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url


class WoolSupplierUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = WoolSupplier
    form_class = WoolSupplierForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل بيانات مورد خيط: ' + str(self.object)
        context['message'] = 'update'
        context['action_url'] = reverse_lazy('Wool:WoolSupplierUpdate', kwargs={'pk': self.object.id})
        return context

    def get_success_url(self, **kwargs):
        messages.success(self.request, "تم تعديل بيانات مورد خيط بنجاح", extra_tags="success")
        return reverse('Wool:WoolSupplierList')


class WoolSupplierDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = WoolSupplier
    form_class = WoolSupplierDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Wool:WoolSupplierList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف مورد خيط: ' + str(self.object)
        context['message'] = 'delete'
        context['action_url'] = reverse_lazy('Wool:WoolSupplierDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف مورد خيط " + str(self.object) + ' بنجاح ', extra_tags="danger")
        myform = WoolSupplier.objects.get(id=self.kwargs['pk'])
        myform.deleted = 1
        myform.save()
        return redirect(self.get_success_url())


class WoolSupplierRestore(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = WoolSupplier
    form_class = WoolSupplierDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Wool:WoolSupplierTrashList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'استرجاع مورد خيط: ' + str(self.object)
        context['message'] = 'restore'
        context['action_url'] = reverse_lazy('Wool:WoolSupplierRestore', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم استرجاع مورد خيط " + str(self.object) + ' بنجاح ', extra_tags="dark")
        myform = WoolSupplier.objects.get(id=self.kwargs['pk'])
        myform.deleted = 0
        myform.save()
        return redirect(self.get_success_url())


class WoolSupplierSuperDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = WoolSupplier
    form_class = WoolSupplierDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Wool:WoolSupplierTrashList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف مورد خيط : ' + str(self.object.id) + 'بشكل نهائي'
        context['message'] = 'super_delete'
        context['action_url'] = reverse_lazy('Wool:WoolSupplierSuperDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف مورد خيط " + str(self.object) + " نهائيا بنجاح ", extra_tags="success")
        my_form = WoolSupplier.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect(self.get_success_url())


def WoolSupplierQuantityDetail(request, pk):
    supplier = WoolSupplier.objects.get(id=pk)
    quantity = WoolSupplierQuantity.objects.filter(supplier=supplier)

    form = WoolSupplierQuantityForm()

    action_url = reverse_lazy('Wool:AddWoolSupplierQuantity', kwargs={'pk': supplier.id})

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

    context = {
        'supplier': supplier,
        'quantity': quantity,
        'form': form,
        'action_url': action_url,
        'system_info': system_info,
        'date': datetime.now().date(),
    }
    return render(request, 'WoolSupplier/supplier_qunatity.html', context)


def AddWoolSupplierQuantity(request, pk):
    supplier = WoolSupplier.objects.get(id=pk)
    form = WoolSupplierQuantityForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.supplier = supplier
        obj.admin = request.user
        obj.save()
        messages.success(request, " تم اضافة كمية جديدة بنجاح ", extra_tags="success")
    else:
        messages.error(request, " دث خطأ أثناء اضافة الكمية ", extra_tags="danger")
    return redirect('Wool:WoolSupplierQuantity', pk=supplier.id)


def DelWoolSupplierQuantity(request, pk):
    quant = WoolSupplierQuantity.objects.get(id=pk)
    id = quant.supplier.id
    quant.delete()
    messages.success(request, " تم حذف كمية بنجاح ", extra_tags="success")
    return redirect('Wool:WoolSupplierQuantity', pk=id)


def WoolSupplierPaymentDetail(request, pk):
    supplier = WoolSupplier.objects.get(id=pk)
    payment = WoolSupplierPayment.objects.filter(supplier=supplier)

    form = WoolSupplierPaymentForm()
    action_url = reverse_lazy('Wool:AddWoolSupplierPayment', kwargs={'pk': supplier.id})

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

    context = {
        'supplier': supplier,
        'payment': payment,
        'form': form,
        'action_url': action_url,
        'system_info': system_info,
        'date': datetime.now().date(),
    }
    return render(request, 'WoolSupplier/supplier_payment.html', context)


def AddWoolSupplierPayment(request, pk):
    supplier = WoolSupplier.objects.get(id=pk)
    form = WoolSupplierPaymentForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.supplier = supplier
        obj.admin = request.user
        obj.save()
        messages.success(request, " تم اضافة دفعة جديدة بنجاح ", extra_tags="success")
    else:
        messages.error(request, " حدث خطأ أثناء اضافة الدفعة ", extra_tags="danger")
    return redirect('Wool:WoolSupplierPayment', pk=supplier.id)


def DelWoolSupplierPayment(request, pk):
    pay = WoolSupplierPayment.objects.get(id=pk)
    id = pay.supplier.id
    pay.delete()
    messages.success(request, " تم حذف دفعة بنجاح ", extra_tags="success")
    return redirect('Wool:WoolSupplierPayment', pk=id)


def PrintWoolSupplierAll(request, pk):
    supplier = WoolSupplier.objects.get(id=pk)
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

    quantity = WoolSupplierQuantity.objects.filter(supplier=supplier)
    if quantity:
        weight = quantity.aggregate(sum=Sum('wool_weight')).get('sum')
        account = quantity.aggregate(account=Sum('total_account')).get('account')
    else:
        weight = 0
        account = 0

    payment = WoolSupplierPayment.objects.filter(supplier=supplier)
    if payment:
        total = payment.aggregate(total=Sum('value')).get('total')
    else:
        total = 0

    default_icon = os.path.join(settings.BASE_DIR, 'static', 'assets', 'images', 'new.png')

    context = {
        'quantity': quantity,
        'weight': weight,
        'account': account,
        'payment': payment,
        'total': total,
        'system_info': system_info,
        'date': datetime.now(),
        'user': request.user.username,
        'supplier': supplier,
        'default_icon': default_icon,
    }
    html_string = render_to_string('WoolSupplier_Reports/print_supplier_details.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    # pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/invoice_pdf.css')], presentational_hints=True)
    css_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'css', 'invoice_pdf.css')
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS(css_path)], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    # modal
    response['Content-Disposition'] = 'inline; filename="treasury_report.pdf"'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response