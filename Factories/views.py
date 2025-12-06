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


class FactoryList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Factory
    paginate_by = 12
    template_name = 'Factory/factory_list.html'
    
    def get_queryset(self):
        qureyset = self.model.objects.filter(deleted=False).order_by('-id')
        return qureyset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'list'
        context['title'] = 'قائمة المصانع'
        context['icons'] = '<i class="fas fa-shapes"></i>'
        context['page'] = 'active'
        context['count'] = self.model.objects.filter(deleted=False).count()
        return context


class FactoryDetails(LoginRequiredMixin, DetailView):
    login_url = '/auth/login'
    model = Factory
    template_name = 'Factory/factory_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'list'
        context['factory'] = self.object

        # factory payment
        queryset_payment = Payment.objects.filter(factory=self.object)
        payment_sum = queryset_payment.aggregate(price=Sum('price')).get('price')
        total_account = FactoryInSide.objects.filter(factory=self.object).aggregate(total=Sum('total_account')).get('total')
        if payment_sum:
            payment_sum = payment_sum
        else:
            payment_sum = 0
        if total_account:
            total_account = total_account
        else:
            total_account = 0
        context['payment'] = queryset_payment.order_by('-date', '-id')
        context['payment_sum'] = payment_sum
        context['total_account'] = total_account
        context['total'] = total_account - payment_sum
        context['payment_form'] = FactoryPaymentForm(self.request.POST or None)

        # factory outside
        queryset_outside = FactoryOutSide.objects.filter(factory=self.object)
        context['outSide'] = queryset_outside.order_by('-date', '-id')
        sum_weight = queryset_outside.aggregate(weight=Sum('weight')).get('weight')
        if sum_weight:
            context['sum_weight'] = sum_weight
        else:
            context['sum_weight'] = 0
        sum_weight_after = queryset_outside.aggregate(after=Sum('weight_after_loss')).get('after')
        if sum_weight_after:
            context['sum_weight_after'] = sum_weight_after
        else:
            context['sum_weight_after'] = 0
        outside_form = FactoryOutSideForm(self.request.POST or None)
        outside_form.fields['percent_loss'].initial = 0
        context['outside_form'] = outside_form

        # factory inside
        queryset_inside = FactoryInSide.objects.filter(factory=self.object)
        outSide = queryset_outside
        context['inSide'] = queryset_inside.order_by('-date', '-id')
        form_inside = FactoryInSideForm(self.request.POST or None)
        form_inside.fields['hour_price'].initial = self.object.hour_price
        form_inside.fields['product'].queryset = Product.objects.filter(deleted=0)
        context['form_inside'] = form_inside
        sum_outside = outSide.aggregate(out=Sum('weight_after_loss')).get('out')
        if sum_outside:
            context['sum_outside'] = sum_outside
        else:
            context['sum_outside'] = 0
        sum_weightt = queryset_inside.aggregate(weight=Sum('weight')).get('weight')
        if sum_weightt:
            context['sum_weightt'] = sum_weightt
        else:
            context['sum_weightt'] = 0
        sum_weightt_after = queryset_inside.aggregate(after=Sum('total_account')).get('after')
        if sum_weightt_after:
            context['sum_weightt_after'] = sum_weightt_after
        else:
            context['sum_weightt_after'] = 0
        products_count = queryset_inside.aggregate(product_count=Sum('product_count')).get('product_count')
        if products_count:
            context['products_count'] = int(products_count)
        else:
            context['products_count'] = 0
        context['products'] = Product.objects.all()

        models_count = queryset_inside.aggregate(model_count=Count('product', distinct=True)).get('model_count')
        if models_count:
            context['models_count'] = int(models_count)
        else:
            context['models_count'] = 0

        hours_count = queryset_inside.aggregate(hour_count=Sum('hour_count')).get('hour_count')
        if hours_count:
            hours_count = "{:.2f}".format(hours_count).split('.')
            only_hours = int(hours_count[0])
            only_minutes = int(hours_count[1])
            if int(only_minutes) > 0:
                hours = int(only_minutes) // 60
                minutes = int(only_minutes) % 60
            else:
                hours = 0
                minutes = 0
            context['hours_count'] = only_hours + hours
            context['minutes_count'] = minutes
        else:
            context['hours_count'] = 0
            context['minutes_count'] = 0

        # reports
        context['form'] = FactoryPaymentReportForm()

        if queryset_payment:
            context['last_payment_id'] = queryset_payment.last().id
        if queryset_outside:
            context['last_outside_id'] = queryset_outside.last().id
        if queryset_inside:
            context['last_inside_id'] = queryset_inside.last().id
        return context


class FactoryTrachList(LoginRequiredMixin, ListView):
    login_url = '/auth/login'
    model = Factory
    paginate_by = 12
    template_name = 'Factory/factory_list.html'
    
    def get_queryset(self):
        queyset = self.model.objects.filter(deleted=True).order_by('-id')
        return queyset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'trach'
        context['count'] = self.model.objects.filter(deleted=True).count()
        return context


class FactoryCreate(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = Factory
    form_class = FactoryForm
    template_name = 'forms/factory_form.html'
    success_url = reverse_lazy('Factories:FactoryList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'اضافة مصنع جديد'
        context['message'] = 'add'
        context['action_url'] = reverse_lazy('Factories:FactoryCreate')
        return context
    
    def get_success_url(self):
        messages.success(self.request, "تم اضافة مصنع جديد", extra_tags="success")

        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url
        

class FactoryUpdate(LoginRequiredMixin ,UpdateView):
    login_url = '/auth/login/'
    model = Factory
    form_class = FactoryForm
    template_name = 'forms/factory_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل مصنع: ' + str(self.object)
        context['message'] = 'update'
        context['action_url'] = reverse_lazy('Factories:FactoryUpdate', kwargs={'pk': self.object.id})
        return context
    
    def get_success_url(self):
        messages.success(self.request,  "تم تعديل المصنع " + str(self.object) + " بنجاح ", extra_tags="success")
        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url
                

class FactoryDelete(LoginRequiredMixin ,UpdateView):
    login_url = '/auth/login/'
    model = Factory
    form_class = FactoryDeleteForm
    template_name = 'forms/factory_form.html'
    

    def get_success_url(self):
        return reverse('Factories:FactoryList')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'نقل المصنع الي سلة المهملات: ' + str(self.object)
        context['message'] = 'delete'
        context['action_url'] = reverse_lazy('Factories:FactoryDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم نقل المصنع " + str(self.object) + ' الي سلة المهملات بنجاح ' , extra_tags="success")
        myform = Factory.objects.get(id=self.kwargs['pk'])
        myform.deleted = 1
        myform.save()
        return redirect(self.get_success_url())        


class FactoryRestore(LoginRequiredMixin ,UpdateView):
    login_url = '/auth/login/'
    model = Factory
    form_class = FactoryDeleteForm
    template_name = 'forms/factory_form.html'
    

    def get_success_url(self):
        return reverse('Factories:FactoryList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'استرجاع مصنع: ' + str(self.object)
        context['message'] = 'restore'
        context['action_url'] = reverse_lazy('Factories:FactoryRestore', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم ارجاع المصنع " + str(self.object) + ' الي القائمة بنجاح ' , extra_tags="success")
        myform = Factory.objects.get(id=self.kwargs['pk'])
        myform.deleted = 0
        myform.save()
        return redirect(self.get_success_url())
    

class FactorySuperDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Factory
    form_class = FactoryDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Factories:FactoryTrachList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف المصنع : ' + str(self.object)
        context['message'] = 'super_delete'
        context['action_url'] = reverse_lazy('Factories:FactorySuperDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف المصنع " + str(self.object) + " نهائيا بنجاح ", extra_tags="success")
        my_form = Factory.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect(self.get_success_url())


class FactoryInSide_div(LoginRequiredMixin, DetailView):
    login_url = '/auth/login/'
    model = Factory
    template_name = 'Factory/inside_div.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_inside = FactoryInSide.objects.filter(factory=self.object)
        if queryset_inside:
            context['last_inside_id'] = queryset_inside.last().id
        product_id = self.request.GET.get('product_id')
        date_val = self.request.GET.get('date_val')
        wool_val = self.request.GET.get('wool_val')
        if product_id:
            product = Product.objects.get(id=int(product_id))
            queryset_inside = queryset_inside.filter(product=product)
        if date_val:
            queryset_inside = queryset_inside.filter(date=date_val)
        if wool_val:
            queryset_inside = queryset_inside.filter(wool_type=int(wool_val))
        outSide = FactoryOutSide.objects.filter(factory=self.object)

        context['inSide'] = queryset_inside.order_by('-date', '-id')
        sum_outside = outSide.aggregate(out=Sum('weight_after_loss')).get('out')
        if sum_outside:
            context['sum_outside'] = sum_outside
        else:
            context['sum_outside'] = 0
        sum_weightt = queryset_inside.aggregate(weight=Sum('weight')).get('weight')
        if sum_weightt:
            context['sum_weightt'] = sum_weightt
        else:
            context['sum_weightt'] = 0
        sum_weightt_after = queryset_inside.aggregate(after=Sum('total_account')).get('after')
        if sum_weightt_after:
            context['sum_weightt_after'] = sum_weightt_after
        else:
            context['sum_weightt_after'] = 0
        products_count = queryset_inside.aggregate(product_count=Sum('product_count')).get('product_count')
        if products_count:
            context['products_count'] = int(products_count)
        else:
            context['products_count'] = 0
        context['factory'] = self.object
        context['type'] = 'list'
        context['products'] = Product.objects.all()

        models_count = queryset_inside.aggregate(model_count=Count('product', distinct=True)).get('model_count')
        if models_count:
            context['models_count'] = int(models_count)
        else:
            context['models_count'] = 0

        hours_count = queryset_inside.aggregate(hour_count=Sum('hour_count')).get('hour_count')
        if hours_count:
            hours_count = "{:.2f}".format(hours_count).split('.')
            only_hours = int(hours_count[0])
            only_minutes = int(hours_count[1])
            if int(only_minutes) > 0:
                hours = int(only_minutes) // 60
                minutes = int(only_minutes) % 60
            else:
                hours = 0
                minutes = 0
            context['hours_count'] = only_hours + hours
            context['minutes_count'] = minutes
        else:
            context['hours_count'] = 0
            context['minutes_count'] = 0

        return context


class FactoryOutSide_div(LoginRequiredMixin, DetailView):
    login_url = '/auth/login/'
    model = Factory
    template_name = 'Factory/outside_div.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_outside = FactoryOutSide.objects.filter(factory=self.object)
        if queryset_outside:
            context['last_outside_id'] = queryset_outside.last().id
        wool_val = self.request.GET.get('wool_val')
        date_val = self.request.GET.get('date_val')
        if wool_val:
            queryset_outside = queryset_outside.filter(wool_type=int(wool_val))
        if date_val:
            queryset_outside = queryset_outside.filter(date=date_val)

        context['outSide'] = queryset_outside.order_by('-date', '-id')
        sum_weight = queryset_outside.aggregate(weight=Sum('weight')).get('weight')
        if sum_weight:
            context['sum_weight'] = sum_weight
        else:
            context['sum_weight'] = 0
        sum_weight_after = queryset_outside.aggregate(after=Sum('weight_after_loss')).get('after')
        if sum_weight_after:
            context['sum_weight_after'] = sum_weight_after
        else:
            context['sum_weight_after'] = 0
        context['type'] = 'list'
        context['factory'] = self.object

        return context


class FactoryPayment_div(LoginRequiredMixin, DetailView):
    login_url = '/auth/login/'
    model = Factory
    template_name = 'Factory/payment_div.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_payment = Payment.objects.filter(factory=self.object)
        if queryset_payment:
            context['last_payment_id'] = queryset_payment.last().id
        date_val = self.request.GET.get('date_val')
        if date_val:
            queryset_payment = queryset_payment.filter(date=date_val)
        payment_sum = queryset_payment.aggregate(price=Sum('price')).get('price')
        total_account =FactoryInSide.objects.filter(factory=self.object).aggregate(total=Sum('total_account')).get('total')
        if payment_sum:
            payment_sum = payment_sum
        else:
            payment_sum = 0
        if total_account:
            total_account = total_account
        else:
            total_account = 0

        context['payment'] = queryset_payment.order_by('-date', '-id')
        context['payment_sum'] = payment_sum
        context['total_account'] = total_account
        context['total'] = total_account - payment_sum
        context['type'] = 'list'
        context['factory'] = self.object
        return context


def FactoryInSideCreate(request):
    if request.is_ajax():
        factory_id = request.POST.get('id')
        factory = Factory.objects.get(id=factory_id)
        date = request.POST.get('date')
        weight = request.POST.get('weight')
        color = request.POST.get('color')
        wool_type = request.POST.get('wool_type')
        product = request.POST.get('product')
        product_weight = request.POST.get('product_weight')
        product_time = request.POST.get('product_time')
        product_count = request.POST.get('product_count')
        hour_count = request.POST.get('hour_count')
        hour_price = request.POST.get('hour_price')
        total_account = request.POST.get('total_account')

        if factory_id and date and product and weight and product_weight and product_count and product_time and hour_count and hour_price and total_account:

            obj = FactoryInSide()
            obj.factory = factory
            obj.date = date
            if weight:
                obj.weight = weight
            else:
                obj.weight = 0
            obj.color = color
            if wool_type:
                obj.wool_type = wool_type
            else:
                obj.wool_type = None
            obj.product = Product.objects.get(id=product)
            obj.product_weight = product_weight
            obj.product_time = product_time
            obj.product_count = product_count
            obj.hour_count = hour_count
            obj.hour_price = hour_price
            obj.total_account = total_account
            obj.admin = request.user
            obj.save()

            if obj:
                response = {
                    'msg': 1
                }

            # prod = obj.product
            # if prod.quantity:
            #     prod.quantity += int(obj.product_count)
            # else:
            #     prod.quantity = int(obj.product_count)
            # prod.save(update_fields=['quantity'])

        else:
            response = {
                'msg': 0
            }
        return JsonResponse(response)


def FactoryInsideDelete(request):
    if request.is_ajax():
        inside_id = request.POST.get('inside_id')
        obj = FactoryInSide.objects.get(id=inside_id)
        obj.delete()

        response = {
            'msg': 'Send Successfully'
        }

        return JsonResponse(response)


def FactoryOutSideCreate(request):
    if request.is_ajax():
        factory_id = request.POST.get('id')
        factory = Factory.objects.get(id=factory_id)

        date = request.POST.get('date')
        weight = request.POST.get('weight')
        color = request.POST.get('color')
        wool_type = request.POST.get('wool_type')
        percent_loss = request.POST.get('percent_loss')
        weight_after_loss = request.POST.get('weight_after_loss')

        if factory_id and date and weight and percent_loss and weight_after_loss:
            obj = FactoryOutSide()
            obj.factory = factory
            obj.date = date
            obj.admin = request.user
            obj.weight = weight
            obj.color = color
            if wool_type:
                obj.wool_type = wool_type
            else:
                obj.wool_type = None
            obj.percent_loss = percent_loss
            obj.weight_after_loss = weight_after_loss
            obj.save()

            if obj:
                response = {
                    'msg': 1
                }
        else:
            response = {
                'msg': 0
            }
        return JsonResponse(response)


def FactoryOutsideDelete(request):
    if request.is_ajax():
        outside_id = request.POST.get('outside_id')
        obj = FactoryOutSide.objects.get(id=outside_id)
        obj.delete()

        if obj:
            response = {
                'msg': 'Send Successfully'
            }

        return JsonResponse(response)


def FactoryPaymentCreate(request):
    if request.is_ajax():
        factory_id = request.POST.get('id')
        factory = Factory.objects.get(id=factory_id)
        
        date = request.POST.get('date')
        recipient = request.POST.get('recipient')
        price = request.POST.get('price')
        
        if factory_id and date and price:
            obj = Payment()
            obj.factory = factory
            obj.date = date
            obj.admin = request.user
            obj.recipient = recipient
            obj.price = price
            obj.save()
            
            if obj:
                response = {
                    'msg' : 1
                }
        else:
            response = {
                'msg' : 0
            }
        return JsonResponse(response)

    
def FactoryPaymentDelete(request):
    if request.is_ajax():
        payment_id = request.POST.get('payment_id')
        obj =  Payment.objects.get(id=payment_id)
        obj.delete()
        
        if obj:
            response = {
                'msg' : 'Send Successfully'
            }

        return JsonResponse(response)


def PrintInside(request, pk):
    factory = Factory.objects.get(id=pk)
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

    queryset = FactoryInSide.objects.filter(factory=pk).order_by('-date', '-id')
    if request.GET.get('from_date'):
        queryset = queryset.filter(date__gte=request.GET.get('from_date'))
    if request.GET.get('to_date'):
        queryset = queryset.filter(date__lte=request.GET.get('to_date'))

    if queryset:
        prods = queryset.aggregate(product=Count('product', distinct=True)).get('product')
        weight = queryset.aggregate(weight=Sum('weight')).get('weight')
        sum_weight = queryset.aggregate(out=Sum('total_account')).get('out')
        sum_count = queryset.aggregate(count=Sum('product_count')).get('count')
        sum_hours = queryset.aggregate(hour=Sum('hour_count')).get('hour')
    else:
        prods = 0
        weight = 0
        sum_weight = 0
        sum_count = 0
        sum_hours = 0

    default_icon = os.path.join(settings.BASE_DIR, 'static', 'assets', 'images', 'new.png')

    context = {
        'queryset': queryset,
        'sum_weight': sum_weight,
        'sum_count': sum_count,
        'sum_hours': sum_hours,
        'prods': prods,
        'weight': weight,
        'system_info': system_info,
        'date': datetime.now(),
        'user': request.user.username,
        'from_date': request.GET.get('from_date'),
        'to_date': request.GET.get('to_date'),
        'factory': factory,
        'default_icon': default_icon,
    }
    html_string = render_to_string('Factory_Reports/print_inside.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    # pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/invoice_pdf.css')], presentational_hints=True)
    css_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'css', 'invoice_pdf.css')
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS(css_path)], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    # modal
    response['Content-Disposition'] = 'inline; filename="treasury_report.pdf"'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def PrintOutside(request, pk):
    factory = Factory.objects.get(id=pk)
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

    queryset = FactoryOutSide.objects.filter(factory=pk).order_by('-date', '-id')
    if request.GET.get('from_date'):
        queryset = queryset.filter(date__gte=request.GET.get('from_date'))
    if request.GET.get('to_date'):
        queryset = queryset.filter(date__lte=request.GET.get('to_date'))

    if queryset:
        sum_all_weight = queryset.aggregate(all=Sum('weight')).get('all')
        sum_weight = queryset.aggregate(out=Sum('weight_after_loss')).get('out')
    else:
        sum_all_weight = 0
        sum_weight = 0

    default_icon = os.path.join(settings.BASE_DIR, 'static', 'assets', 'images', 'new.png')

    context = {
        'queryset': queryset,
        'sum_all_weight': sum_all_weight,
        'sum_weight': sum_weight,
        'system_info': system_info,
        'date': datetime.now(),
        'user': request.user.username,
        'from_date': request.GET.get('from_date'),
        'to_date': request.GET.get('to_date'),
        'factory': factory,
        'default_icon': default_icon,
    }
    html_string = render_to_string('Factory_Reports/print_outside.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    # pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/invoice_pdf.css')], presentational_hints=True)
    css_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'css', 'invoice_pdf.css')
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS(css_path)], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    # modal
    response['Content-Disposition'] = 'inline; filename="treasury_report.pdf"'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def PrintPayment(request,pk):
    factory = Factory.objects.get(id=pk)
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

    print(request.GET.get('from_date'))
    print(request.GET.get('to_date'))
    queryset = Payment.objects.filter(factory=pk).order_by('-date', '-id')
    if request.GET.get('from_date'):
        queryset = queryset.filter(date__gte=request.GET.get('from_date'))
    if request.GET.get('to_date'):
        queryset = queryset.filter(date__lte=request.GET.get('to_date'))

    if queryset:
        count_price = queryset.aggregate(price=Sum('price')).get('price')
    else:
        count_price = 0

    default_icon = os.path.join(settings.BASE_DIR, 'static', 'assets', 'images', 'new.png')

    context = {
        'queryset':queryset,
        'count_price': count_price,
        'system_info': system_info,
        'date': datetime.now(),
        'user': request.user.username,
        'from_date': request.GET.get('from_date'),
        'to_date': request.GET.get('to_date'),
        'factory':factory,
        'default_icon': default_icon,
    }
    html_string = render_to_string('Factory_Reports/print_payment.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    # pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/invoice_pdf.css')], presentational_hints=True)
    css_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'css', 'invoice_pdf.css')
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS(css_path)], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    # modal
    response['Content-Disposition'] = 'inline; filename="treasury_report.pdf"'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def PrintAll(request, pk):
    factory = Factory.objects.get(id=pk)
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

    inside = FactoryInSide.objects.filter(factory=pk)
    if inside:
        sum_in_weight = inside.aggregate(weight=Sum('weight')).get('weight')
        sum_in_total = inside.aggregate(total=Sum('total_account')).get('total')
        sum_product_count = inside.aggregate(count=Sum('product_count')).get('count')
        sum_hours = inside.aggregate(hour=Sum('hour_count')).get('hour')
        count_models = inside.aggregate(models=Count('product', distinct=True)).get('models')

        sum_hours = "{:.2f}".format(sum_hours).split('.')
        only_hours = int(sum_hours[0])
        only_minutes = int(sum_hours[1])
        if int(only_minutes) > 0:
            hours = int(only_minutes) // 60
            minutes = int(only_minutes) % 60
        else:
            hours = 0
            minutes = 0
        sum_hours = only_hours + hours
        sum_minutes = minutes
    else:
        sum_in_weight = 0
        sum_in_total = 0
        sum_product_count = 0
        sum_hours = 0
        sum_minutes = 0
        count_models = 0

    outside = FactoryOutSide.objects.filter(factory=pk)
    if outside:
        sum_out_weight = outside.aggregate(out=Sum('weight_after_loss')).get('out')
    else:
        sum_out_weight = 0

    payment = Payment.objects.filter(factory=pk)
    if payment:
        sum_out_total = payment.aggregate(price=Sum('price')).get('price')
    else:
        sum_out_total = 0

    default_icon = os.path.join(settings.BASE_DIR, 'static', 'assets', 'images', 'new.png')

    context = {
        'sum_in_weight': sum_in_weight,
        'sum_in_total': sum_in_total,
        'sum_product_count': sum_product_count,
        'sum_hours': sum_hours,
        'sum_minutes': sum_minutes,
        'count_models': count_models,
        'sum_out_weight': sum_out_weight,
        'sum_out_total': sum_out_total,
        'system_info': system_info,
        'date': datetime.now(),
        'user': request.user.username,
        'factory': factory,
        'default_icon': default_icon,
    }
    html_string = render_to_string('Factory_Reports/print_factory_details.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    # pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/invoice_pdf.css')], presentational_hints=True)
    css_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'css', 'invoice_pdf.css')
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS(css_path)], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    # modal
    response['Content-Disposition'] = 'inline; filename="treasury_report.pdf"'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def get_product_weight_time(request):
    e = request.GET.get('e')
    product = Product.objects.get(id=int(e))
    if product.weight:
        weight = product.weight
    else:
        weight = 0.0
    if product.time:
        time = product.time
    else:
        time = 0.0
    data = json.dumps({
        'prod_weight': weight,
        'prod_time': time,
    })
    return HttpResponse(data, content_type='application/json')


def UpdateFactoryOutsideLoss(request, pk):
    new_percent_loss = request.POST.get('new_percent_loss')
    outsides = FactoryOutSide.objects.filter(factory__id=pk)
    for outside in outsides:
        outside.percent_loss = new_percent_loss
        outside.weight_after_loss = (float(outside.weight) - (float(outside.weight) * float(outside.percent_loss)) / 100)
        outside.save(update_fields=['percent_loss', 'weight_after_loss'])
    messages.success(request, "تم تعديل نسبة الهالك بنجاح", extra_tags="success")
    return redirect('Factories:FactoryDetails', pk=pk)


def UpdateFactoryHourPrice(request, pk):
    new_hour_price = request.POST.get('new_hour_price_input')
    factory_inside_objects = FactoryInSide.objects.filter(factory__id=pk)
    for inside_object in factory_inside_objects:
        hour_count = inside_object.product_count * inside_object.product_time / 60
        inside_object.hour_price = new_hour_price
        total = "{:.2f}".format(float(new_hour_price) * float(hour_count))
        inside_object.total_account = total
        inside_object.save(update_fields=['hour_price', 'total_account'])
    messages.success(request, "تم تعديل سعر الساعه بنجاح", extra_tags="success")
    return redirect('Factories:FactoryDetails', pk=pk)

############################################################


class SupplierList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Supplier
    paginate_by = 12
    template_name = 'Supplier/supplier_list.html'

    def get_queryset(self):
        queryset = self.model.objects.filter(deleted=False, type=int(self.kwargs['type'])).order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['type'] = self.kwargs['type']
        context['count'] = self.model.objects.filter(deleted=False, type=int(self.kwargs['type'])).count()
        return context


class SupplierTrashList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Supplier
    paginate_by = 12
    template_name = 'Supplier/supplier_list.html'

    def get_queryset(self):
        queryset = self.model.objects.filter(deleted=True, type=int(self.kwargs['type'])).order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'trash'
        context['type'] = self.kwargs['type']
        context['count'] = self.model.objects.filter(deleted=True, type=int(self.kwargs['type'])).count()
        return context


class SupplierCreate(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = Supplier
    form_class = SupplierForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs['type'] == 1:
            context['title'] = 'اضافة مورد'
        else:
            context['title'] = 'اضافة مستورد'
        context['message'] = 'create'
        context['action_url'] = reverse_lazy('Factories:SupplierCreate', kwargs={'type': self.kwargs['type']})
        return context

    def form_valid(self, form):
        form.save()
        obj = form.save(commit=False)
        myform = Supplier.objects.get(id=obj.id)
        myform.type = int(self.kwargs['type'])
        myform.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        if self.kwargs['type'] == 1:
            messages.success(self.request, "تم اضافة مورد جديد", extra_tags="success")
        else:
            messages.success(self.request, "تم اضافة مستورد جديد", extra_tags="success")

        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url


class SupplierUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Supplier
    form_class = SupplierForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.type == 1:
            context['title'] = 'تعديل بيانات مورد: ' + str(self.object)
        else:
            context['title'] = 'تعديل بيانات مستورد: ' + str(self.object)
        context['message'] = 'update'
        context['action_url'] = reverse_lazy('Factories:SupplierUpdate', kwargs={'pk': self.object.id})
        return context

    def get_success_url(self, **kwargs):
        if self.object.type == 1:
            messages.success(self.request, "تم تعديل بيانات مورد بنجاح", extra_tags="success")
        else:
            messages.success(self.request, "تم تعديل بيانات مستورد بنجاح", extra_tags="success")
        return reverse('Factories:SupplierList', kwargs={'type': self.object.type})


class SupplierDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Supplier
    form_class = SupplierDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Factories:SupplierList', kwargs={'type': self.object.type})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.type == 1:
            context['title'] = 'حذف مورد: ' + str(self.object)
        else:
            context['title'] = 'حذف مستورد: ' + str(self.object)
        context['message'] = 'delete'
        context['action_url'] = reverse_lazy('Factories:SupplierDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        if self.object.type == 1:
            messages.success(self.request, " تم حذف مورد " + str(self.object) + ' بنجاح ', extra_tags="danger")
        else:
            messages.success(self.request, " تم حذف مستورد " + str(self.object) + ' بنجاح ', extra_tags="danger")
        myform = Supplier.objects.get(id=self.kwargs['pk'])
        myform.deleted = 1
        myform.save()
        return redirect(self.get_success_url())


class SupplierRestore(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Supplier
    form_class = SupplierDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Factories:SupplierTrashList', kwargs={'type': self.object.type})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.type == 1:
            context['title'] = 'استرجاع مورد: ' + str(self.object)
        else:
            context['title'] = 'استرجاع مستورد: ' + str(self.object)
        context['message'] = 'restore'
        context['action_url'] = reverse_lazy('Factories:SupplierRestore', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        if self.object.type == 1:
            messages.success(self.request, " تم استرجاع مورد " + str(self.object) + ' بنجاح ', extra_tags="dark")
        else:
            messages.success(self.request, " تم استرجاع مستورد " + str(self.object) + ' بنجاح ', extra_tags="dark")
        myform = Supplier.objects.get(id=self.kwargs['pk'])
        myform.deleted = 0
        myform.save()
        return redirect(self.get_success_url())


class SupplierSuperDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Supplier
    form_class = SupplierDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Factories:SupplierTrashList', kwargs={'type': self.object.type})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.type == 1:
            context['title'] = 'حذف مورد : ' + str(self.object.id) + 'بشكل نهائي'
        else:
            context['title'] = 'حذف مستورد : ' + str(self.object.id) + 'بشكل نهائي'
        context['message'] = 'super_delete'
        context['action_url'] = reverse_lazy('Factories:SupplierSuperDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        if self.object.type == 1:
            messages.success(self.request, " تم حذف مورد " + str(self.object) + " نهائيا بنجاح ", extra_tags="success")
        else:
            messages.success(self.request, " تم حذف مستورد " + str(self.object) + " نهائيا بنجاح ", extra_tags="success")
        my_form = Supplier.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect(self.get_success_url())


def SupplierQuantityDetail(request, pk):
    supplier = Supplier.objects.get(id=pk)
    quantity = SupplierQuantity.objects.filter(supplier=supplier)
    quantity_prods = quantity.values_list('product__name', flat=True).distinct()

    form = SupplierQuantityForm()
    form.fields['product'].queryset = Product.objects.filter(deleted=False)

    action_url = reverse_lazy('Factories:AddSupplierQuantity', kwargs={'pk': supplier.id})

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
        'quantity_prods': quantity_prods,
        'form': form,
        'action_url': action_url,
        'system_info': system_info,
        'date': datetime.now().date(),
    }
    return render(request, 'Supplier/supplier_qunatity.html', context)


def AddSupplierQuantity(request, pk):
    supplier = Supplier.objects.get(id=pk)
    form = SupplierQuantityForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.supplier = supplier
        obj.admin = request.user
        obj.save()
        messages.success(request, " تم اضافة كمية جديدة بنجاح ", extra_tags="success")
    else:
        messages.error(request, " دث خطأ أثناء اضافة الكمية ", extra_tags="danger")
    return redirect('Factories:SupplierQuantity', pk=supplier.id)


def DelSupplierQuantity(request, pk):
    quant = SupplierQuantity.objects.get(id=pk)
    id = quant.supplier.id
    quant.delete()
    messages.success(request, " تم حذف كمية بنجاح ", extra_tags="success")
    return redirect('Factories:SupplierQuantity', pk=id)


def SupplierPaymentDetail(request, pk):
    supplier = Supplier.objects.get(id=pk)
    payment = SupplierPayment.objects.filter(supplier=supplier)

    form = SupplierPaymentForm()
    action_url = reverse_lazy('Factories:AddSupplierPayment', kwargs={'pk': supplier.id})

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
    return render(request, 'Supplier/supplier_payment.html', context)


def AddSupplierPayment(request, pk):
    supplier = Supplier.objects.get(id=pk)
    form = SupplierPaymentForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.supplier = supplier
        obj.admin = request.user
        obj.save()
        messages.success(request, " تم اضافة دفعة جديدة بنجاح ", extra_tags="success")
    else:
        messages.error(request, " حدث خطأ أثناء اضافة الدفعة ", extra_tags="danger")
    return redirect('Factories:SupplierPayment', pk=supplier.id)


def DelSupplierPayment(request, pk):
    pay = SupplierPayment.objects.get(id=pk)
    id = pay.supplier.id
    pay.delete()
    messages.success(request, " تم حذف دفعة بنجاح ", extra_tags="success")
    return redirect('Factories:SupplierPayment', pk=id)


def PrintSupplierAll(request, pk):
    supplier = Supplier.objects.get(id=pk)
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

    quantity = SupplierQuantity.objects.filter(supplier=supplier)
    if quantity:
        count = quantity.aggregate(count=Sum('product_count')).get('count')
        account = quantity.aggregate(account=Sum('total_account')).get('account')
    else:
        count = 0
        account = 0

    payment = SupplierPayment.objects.filter(supplier=supplier)
    if payment:
        total = payment.aggregate(total=Sum('value')).get('total')
    else:
        total = 0

    default_icon = os.path.join(settings.BASE_DIR, 'static', 'assets', 'images', 'new.png')

    context = {
        'quantity': quantity,
        'count': count,
        'account': account,
        'payment': payment,
        'total': total,
        'system_info': system_info,
        'date': datetime.now(),
        'user': request.user.username,
        'supplier': supplier,
        'default_icon': default_icon,
    }
    html_string = render_to_string('Supplier_Reports/print_supplier_details.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    # pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/invoice_pdf.css')], presentational_hints=True)
    css_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'css', 'invoice_pdf.css')
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS(css_path)], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    # modal
    response['Content-Disposition'] = 'inline; filename="treasury_report.pdf"'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response