import datetime
from decimal import Decimal
from django.db.models.aggregates import Sum, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import  LoginRequiredMixin
from django.views.generic import *

from Core.models import SystemInformation
from .forms import *
from django.contrib import messages
import weasyprint
from django.template.loader import render_to_string
from datetime import datetime


class WorkerList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Worker
    paginate_by = 12
    template_name = 'Worker/worker_list.html'
    
    def get_queryset(self):
        qureyset = self.model.objects.filter(deleted=False).order_by('-id')
        return qureyset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'list'
        context['title'] = 'قائمة العمال'
        context['icons'] = '<i class="fas fa-shapes"></i>'
        context['page'] = 'active'
        context['count'] = self.model.objects.filter(deleted=False).count()
        return context


class WorkerDetails(LoginRequiredMixin, DetailView):
    login_url = '/auth/login'
    model = Worker
    template_name = 'Worker/worker_details.html'

    def get_count_days(self):
        atta = WorkerAttendance.objects.filter(worker=self.object).order_by('-date', '-id')
        if atta != None:
            count_days = atta.count()
        else:
            count_days = 0
        total = {
            'count_days': count_days
        }
        return total

    def get_absent_days(self):
        atta = WorkerAttendance.objects.filter(worker=self.object, attend=False, hour_count=5).order_by('-date', '-id')
        if atta != None:
            count_days = atta.count()
        else:
            count_days = 0
        total = {
            'count_days': count_days
        }
        return total

    def get_real_count_days(self):
        atta = WorkerAttendance.objects.filter(worker=self.object).order_by('-date', '-id')
        if atta != None:
            val = 0
            for item in atta:
                if item.hour_count == 1:
                    hours = 6
                elif item.hour_count == 2:
                    hours = 8
                elif item.hour_count == 3:
                    hours = 12
                elif item.hour_count == 4:
                    hours = 18
                else:
                    hours = 0
                val = val + hours
            count_days = val
            real_days = count_days / 12
            rest_hours = count_days % 12
        else:
            real_days = 0
            rest_hours = 0
        total = {
            'real_days': int(real_days),
            'rest_hours': int(rest_hours)
        }
        return total

    def get_sum_salary(self, **kwargs):
        worker = Worker.objects.get(id=self.object.id)
        worker_price = worker.day_cost

        count_days = self.get_real_count_days()["real_days"]
        count_hours = self.get_real_count_days()["rest_hours"] / 12
        sum_price = count_days * worker_price
        sum_price2 = count_hours * worker_price
        total = {
            'sum_price': sum_price + sum_price2
        }
        return total

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'list'
        context['obj'] = self.object
        context['worker_id'] = self.object.id

        #attendance
        attendance_form = WorkerAttendanceForm(self.request.POST or None)
        attendance_form.fields['hour_count'].initial = 3
        context['attendance_form'] = attendance_form
        attendance_queryset = WorkerAttendance.objects.filter(worker=self.object)
        context['workers'] = attendance_queryset.order_by('-date', '-id')
        context['attendance_summary'] = self.get_count_days()
        context['absence_summary'] = self.get_absent_days()
        context['attendance_real_summary'] = self.get_real_count_days()
        context['attendance_all_cost'] = self.get_sum_salary()

        # production
        production_form = WorkerProductionForm(self.request.POST or None)
        production_form.fields['price'].initial = self.object.day_cost
        production_form.fields['product'].queryset = Product.objects.filter(deleted=0)
        context['production_form'] = production_form
        production_queryset = WorkerProduction.objects.filter(worker=self.object)
        context['production'] = production_queryset.order_by('-date', '-id')
        production_total = production_queryset.aggregate(quantity=Sum('quantity')).get('quantity')
        production_cost = production_queryset.aggregate(total=Sum('total')).get('total')
        if production_total:
            context['production_total'] = production_total
        else:
            context['production_total'] = 0
        if production_cost:
            context['production_cost'] = production_cost
        else:
            context['production_cost'] = 0
        context['products'] = Product.objects.all()

        # payment
        context['payment_form'] = WorkerPaymentForm(self.request.POST or None)
        payment_queryset = WorkerPayment.objects.filter(worker=self.object)
        context['payment'] = payment_queryset.order_by('-date', '-id')
        payment_sum = payment_queryset.aggregate(price=Sum('price')).get('price')
        if payment_sum:
            context['payment_sum'] = payment_sum
        else:
            context['payment_sum'] = 0
        if self.object.worker_type == 5:
            context['payment_all_cost'] = self.get_sum_salary()
        else:
            payment_total = production_queryset.aggregate(total=Sum('total')).get('total')
            if payment_total:
                payment_total = payment_total
            else:
                payment_total = 0
            payment_cost = {
                'sum_price': payment_total
            }
            context['payment_all_cost'] = payment_cost

        # reports
        context['form'] = WorkerPaymentReportForm

        if attendance_queryset:
            context['last_attendance_id'] = attendance_queryset.last().id
        if production_queryset:
            context['last_production_id'] = production_queryset.last().id
        if payment_queryset:
            context['last_payment_id'] = payment_queryset.last().id

        return context


class WorkerTrachList(LoginRequiredMixin, ListView):
    login_url = '/auth/login'
    model = Worker
    paginate_by = 12
    template_name = 'Worker/worker_list.html'
    
    def get_queryset(self):
        queyset = self.model.objects.filter(deleted=True).order_by('-id')
        return queyset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'trach'
        context['count'] = self.model.objects.filter(deleted=True).count()
        return context


class WorkerCreate(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = Worker
    form_class = WorkerForm
    template_name = 'forms/form_template.html'
    success_url = reverse_lazy('Workers:workerList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'اضافة عامل جديد'
        context['message'] = 'add'
        context['action_url'] = reverse_lazy('Workers:WorkerCreate')
        return context
    
    def get_success_url(self):
        messages.success(self.request, "تم اضافة عامل جديد", extra_tags="success")

        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url
        

class WorkerUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Worker
    form_class = WorkerForm
    template_name = 'forms/form_template.html'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل عامل: ' + str(self.object)
        context['message'] = 'update'
        context['action_url'] = reverse_lazy('Workers:WorkerUpdate', kwargs={'pk': self.object.id})
        return context
    
    def get_success_url(self):
        messages.success(self.request,  "تم تعديل العامل " + str(self.object) + " بنجاح ", extra_tags="success")
        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url        
        

class WorkerDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Worker
    form_class = WorkerDeleteForm
    template_name = 'forms/form_template.html'
    

    def get_success_url(self):
        return reverse('Workers:WorkerList')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'نقل العامل الي سلة المهملات: ' + str(self.object)
        context['message'] = 'delete'
        context['action_url'] = reverse_lazy('Workers:WorkerDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم نقل العامل " + str(self.object) + ' الي سلة المهملات بنجاح ' , extra_tags="success")
        myform = Worker.objects.get(id=self.kwargs['pk'])
        myform.deleted = 1
        myform.save()
        return redirect(self.get_success_url())


class WorkerRestore(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Worker
    form_class = WorkerDeleteForm
    template_name = 'forms/form_template.html'
    

    def get_success_url(self):
        return reverse('Workers:WorkerList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'استرجاع العامل: ' + str(self.object)
        context['message'] = 'restore'
        context['action_url'] = reverse_lazy('Workers:WorkerRestore', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم العامل " + str(self.object) + ' الي القائمة بنجاح ' , extra_tags="success")
        myform = Worker.objects.get(id=self.kwargs['pk'])
        myform.deleted = 0
        myform.save()
        return redirect(self.get_success_url())


class WorkerSuperDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Worker
    form_class = WorkerDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Workers:WorkerTrachList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف العامل : ' + str(self.object)
        context['message'] = 'super_delete'
        context['action_url'] = reverse_lazy('Workers:WorkerSuperDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف العامل " + str(self.object) + " نهائيا بنجاح ", extra_tags="success")
        my_form = Worker.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect(self.get_success_url())


class WorkerAttendance_div(LoginRequiredMixin, DetailView):
    login_url = '/auth/login/'
    model = Worker
    template_name = 'Worker/worker_attendance_div.html'

    def get_count_days(self, time_val, date_val):
        atta = WorkerAttendance.objects.filter(worker=self.object).order_by('-date', '-id')
        if time_val:
            atta = atta.filter(hour_count=int(time_val))
        if date_val:
            atta = atta.filter(date=date_val)
        if atta != None:
            count_days = atta.count()
        else:
            count_days = 0
        total = {
            'count_days': count_days
        }
        return total

    def get_absent_days(self, time_val, date_val):
        atta = WorkerAttendance.objects.filter(worker=self.object, attend=False, hour_count=5).order_by('-date', '-id')
        if time_val:
            atta = atta.filter(hour_count=int(time_val))
        if date_val:
            atta = atta.filter(date=date_val)
        if atta != None:
            count_days = atta.count()
        else:
            count_days = 0
        total = {
            'count_days': count_days
        }
        return total

    def get_real_count_days(self, time_val, date_val):
        atta = WorkerAttendance.objects.filter(worker=self.object).order_by('-date', '-id')
        if time_val:
            atta = atta.filter(hour_count=int(time_val))
        if date_val:
            atta = atta.filter(date=date_val)
        if atta != None:
            val = 0
            for item in atta:
                if item.hour_count == 1:
                    hours = 6
                elif item.hour_count == 2:
                    hours = 8
                elif item.hour_count == 3:
                    hours = 12
                elif item.hour_count == 4:
                    hours = 18
                else:
                    hours = 0
                val = val + hours
            count_days = val
            real_days = count_days / 12
            rest_hours = count_days % 12
        else:
            real_days = 0
            rest_hours = 0
        total = {
            'real_days': int(real_days),
            'rest_hours': int(rest_hours)
        }
        return total

    def get_sum_salary(self, time_val, date_val, **kwargs):
        worker = Worker.objects.get(id=self.object.id)
        worker_price = worker.day_cost

        count_days = self.get_real_count_days(time_val, date_val)["real_days"]
        count_hours = self.get_real_count_days(time_val, date_val)["rest_hours"] / 12
        sum_price = count_days * worker_price
        sum_price2 = count_hours * worker_price
        total = {
            'sum_price': sum_price + sum_price2
        }
        return total

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendance_queryset = WorkerAttendance.objects.filter(worker=self.object)
        if attendance_queryset:
            context['last_attendance_id'] = attendance_queryset.last().id

        time_val = self.request.GET.get('time_val')
        date_val = self.request.GET.get('date_val')
        if time_val:
            attendance_queryset = attendance_queryset.filter(hour_count=int(time_val))
        if date_val:
            attendance_queryset = attendance_queryset.filter(date=date_val)

        context['workers'] = attendance_queryset.order_by('-date', '-id')
        context['attendance_summary'] = self.get_count_days(time_val, date_val)
        context['absence_summary'] = self.get_absent_days(time_val, date_val)
        context['attendance_real_summary'] = self.get_real_count_days(time_val, date_val)
        context['attendance_all_cost'] = self.get_sum_salary(time_val, date_val)
        context['type'] = 'list'
        context['obj'] = self.object
        context['worker_id'] = self.object.id

        return context


class Worker_Production_div(LoginRequiredMixin, DetailView):
    login_url = '/auth/login/'
    model = Worker 
    template_name = 'Worker/worker_production_div.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        production_queryset = WorkerProduction.objects.filter(worker=self.object)
        if production_queryset:
            context['last_production_id'] = production_queryset.last().id

        product_id = self.request.GET.get('product_id')
        date_val = self.request.GET.get('date_val')
        if product_id:
            product = Product.objects.get(id=int(product_id))
            production_queryset = production_queryset.filter(product=product)
        if date_val:
            production_queryset = production_queryset.filter(date=date_val)

        context['production'] = production_queryset.order_by('-date', '-id')
        context['type'] = 'list'
        production_total = production_queryset.aggregate(quantity=Sum('quantity')).get('quantity')
        production_cost = production_queryset.aggregate(total=Sum('total')).get('total')
        if production_total:
            context['production_total'] = production_total
        else:
            context['production_total'] = 0
        if production_cost:
            context['production_cost'] = production_cost
        else:
            context['production_cost'] = 0
        context['obj'] = self.object
        context['products'] = Product.objects.all()
        context['worker_id'] = self.object.id

        return context

    
class WorkerPayment_div(LoginRequiredMixin, DetailView):
    login_url = '/auth/login/'
    model = Worker
    template_name = 'Worker/worker_payment_div.html'

    def get_real_count_days(self):
        atta = WorkerAttendance.objects.filter(worker=self.object).order_by('-date', '-id')
        if atta != None:
            val = 0
            for item in atta:
                if item.hour_count == 1:
                    hours = 6
                elif item.hour_count == 2:
                    hours = 8
                elif item.hour_count == 3:
                    hours = 12
                elif item.hour_count == 4:
                    hours = 18
                else:
                    hours = 0
                val = val + hours
            count_days = val
            real_days = count_days / 12
            rest_hours = count_days % 12
        else:
            real_days = 0
            rest_hours = 0
        total = {
            'real_days': int(real_days),
            'rest_hours': int(rest_hours)
        }
        return total

    def get_sum_salary(self, **kwargs):
        worker = Worker.objects.get(id=self.object.id)
        worker_price = worker.day_cost

        count_days = self.get_real_count_days()["real_days"]
        count_hours = self.get_real_count_days()["rest_hours"] / 12
        sum_price = count_days * worker_price
        sum_price2 = count_hours * worker_price
        total = {
            'sum_price': sum_price + sum_price2
        }
        return total

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_queryset = WorkerPayment.objects.filter(worker=self.object)
        if payment_queryset:
            context['last_payment_id'] = payment_queryset.last().id

        date_val = self.request.GET.get('date_val')
        if date_val:
            payment_queryset = payment_queryset.filter(date=date_val)

        context['payment'] = payment_queryset.order_by('-date', '-id')
        payment_sum = payment_queryset.aggregate(price=Sum('price')).get('price')
        if payment_sum:
            context['payment_sum'] = payment_sum
        else:
            context['payment_sum'] = 0
        if self.object.worker_type == 5:
            context['payment_all_cost'] = self.get_sum_salary()
        else:
            payment_total = WorkerProduction.objects.filter(worker=self.object).aggregate(total=Sum('total')).get('total')
            if payment_total:
                payment_total = payment_total
            else:
                payment_total = 0
            payment_cost = {
                'sum_price': payment_total
            }
            context['payment_all_cost'] = payment_cost
        context['type'] = 'list'
        context['obj'] = self.object
        context['worker_id'] = self.object.id

        return context


def WorkerAttendanceCreate(request):
    if request.is_ajax():
        worker_id = request.POST.get('id')
        worker = Worker.objects.get(id=worker_id)
        date = request.POST.get('date')
        day = request.POST.get('day')
        hour_count = request.POST.get('hour_count')
        user = request.user

        attendance_dates = []
        attendance_queryset = WorkerAttendance.objects.filter(worker__id=worker_id)
        if attendance_queryset:
            attendance_dates = attendance_queryset.values_list('date', flat=True)
            attendance_dates = [item.strftime("%Y-%m-%d") for item in attendance_dates]
           
        if date and day and hour_count:
            if not date in attendance_dates:
                obj = WorkerAttendance()
                obj.worker = worker
                obj.date = date
                obj.day = day
                obj.hour_count = hour_count
                if int(hour_count) == 5:
                    obj.attend = False
                else:
                    obj.attend = True
                obj.admin = user
                obj.save()

                if obj:
                    response = {
                        'msg': 1
                    }
            else:
                response = {
                    'msg': -1
                }
        else:
            response = {
                'msg': 0
            }
        return JsonResponse(response)


def WorkerAttendanceDelete(request):
    if request.is_ajax():
        attendance_id = request.POST.get('attendance_id')
        obj = WorkerAttendance.objects.get(id=attendance_id)
        obj.delete()

        if obj:
            response = {
                'msg': 'Send Successfully'
            }

        return JsonResponse(response)


def WorkerProductionCreate(request):
    if request.is_ajax():
        worker_id = request.POST.get('id')
        worker = Worker.objects.get(id=worker_id)

        date = request.POST.get('date')
        day = request.POST.get('day')
        quantity = request.POST.get('worker_quantity')
        price = request.POST.get('worker_price')
        total = request.POST.get('worker_total')
        product = request.POST.get('worker_product')

        if worker and date and day and quantity and price and total:
            obj = WorkerProduction()
            obj.admin = request.user
            obj.date = date
            obj.day = day
            obj.quantity = quantity
            obj.price = price
            obj.total = total
            if product:
                obj.product = Product.objects.get(id=int(product))
            else:
                obj.product = None
            obj.worker = worker
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


def WorkerProductionDelete(request):
    if request.is_ajax():
        production_id = request.POST.get('worker_Production_id')
        obj = WorkerProduction.objects.get(id=production_id)
        obj.delete()

        if obj:
            response = {
                'msg': 'Send Successfully'
            }

        return JsonResponse(response)


def WorkerPaymentCreate(request):
    if request.is_ajax():
        worker_id = request.POST.get('id')
        worker = Worker.objects.get(id=worker_id)
        
        date = request.POST.get('date')
        # admin = request.POST.get('admin')
        # user = User.objects.get(id=admin)
        price = request.POST.get('price')
        description = request.POST.get('description')

        if worker_id and date and price:
            obj = WorkerPayment()
            obj.worker = worker
            obj.date = date
            obj.admin = request.user
            obj.price = price
            obj.description = description
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


def WorkerPaymentDelete(request):
    if request.is_ajax():
        payment_id = request.POST.get('payment_id')
        obj = WorkerPayment.objects.get(id=payment_id)
        obj.delete()
        
        if obj:
            response = {
                'msg' : 'Send Successfully'
            }

        return JsonResponse(response)

    
def PrintWorkerAttendance(request,pk):
    worker = Worker.objects.get(id=pk)
    system_info = SystemInformation.objects.all()
    if system_info.count() > 0:
        system_info = system_info.last()
    else:
        system_info = None
            
    queryset = WorkerAttendance.objects.filter(worker=pk).order_by('-date', '-id')
    if request.GET.get('from_date'):
        queryset = queryset.filter(date__gte = request.GET.get('from_date'))
    if request.GET.get('to_date'):
        queryset = queryset.filter(date__lte = request.GET.get('to_date'))
    
    atta = queryset
    if atta != None:
        val = 0
        for item in atta:
            if item.hour_count == 1:
                hours = 6
            elif item.hour_count == 2:
                hours = 8
            elif item.hour_count == 3:
                hours = 12
            elif item.hour_count == 4:
                hours = 18
            else:
                hours = 0
            val = val + hours
        count_days = val
        real_days = count_days / 12
        rest_hours = count_days % 12
    else:
        real_days = 0
        rest_hours = 0

    context = {
        'queryset':queryset,
        'count_days':  queryset.count,
        'system_info':system_info,
        'date': datetime.now(),
        'user': request.user.username,
        'from_date': request.GET.get('from_date'),
        'to_date': request.GET.get('to_date'),
        'worker':worker,
        'real_days':int(real_days),
        'rest_hours':int(rest_hours),
    }
    html_string = render_to_string('Worker_Reports/print_worker_attendance.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/invoice_pdf.css')], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    return response

      
def PrintWorkerproductions(request,pk):
    worker = Worker.objects.get(id=pk)
    system_info = SystemInformation.objects.all()
    if system_info.count() > 0:
        system_info = system_info.last()
    else:
        system_info = None
            
    queryset = WorkerProduction.objects.filter(worker=pk).order_by('-date', '-id')
    if request.GET.get('from_date'):
        queryset = queryset.filter(date__gte = request.GET.get('from_date'))
    if request.GET.get('to_date'):
        queryset = queryset.filter(date__lte = request.GET.get('to_date'))

    context = {
        'queryset':queryset,
        'total_productions': queryset.aggregate(quantity=Sum('quantity')).get('quantity'),
        'total_cost': queryset.aggregate(total=Sum('total')).get('total'),
        'models_count': queryset.aggregate(models=Count('product', distinct=True)).get('models'),
        'system_info':system_info,
        'date': datetime.now(),
        'user': request.user.username,
        'from_date': request.GET.get('from_date'),
        'to_date': request.GET.get('to_date'),
        'worker':worker,
    }
    html_string = render_to_string('Worker_Reports/print_worker_productions.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/invoice_pdf.css')], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    return response


def PrintWorkerPayment(request, pk):
    worker = Worker.objects.get(id=pk)
    system_info = SystemInformation.objects.all()
    if system_info.count() > 0:
        system_info = system_info.last()
    else:
        system_info = None

    queryset = WorkerPayment.objects.filter(worker=pk).order_by('-date', '-id')
    if request.GET.get('from_date'):
        queryset = queryset.filter(date__gte=request.GET.get('from_date'))
    if request.GET.get('to_date'):
        queryset = queryset.filter(date__lte=request.GET.get('to_date'))

    context = {
        'queryset': queryset,
        'count_price': queryset.aggregate(price=Sum('price')).get('price'),
        'system_info': system_info,
        'date': datetime.now(),
        'user': request.user.username,
        'from_date': request.GET.get('from_date'),
        'to_date': request.GET.get('to_date'),
        'worker': worker,
    }
    html_string = render_to_string('Worker_Reports/print_worker_payment.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/invoice_pdf.css')], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    return response


def PrintWorkerAll(request, pk):
    worker = Worker.objects.get(id=pk)
    system_info = SystemInformation.objects.all()
    if system_info.count() > 0:
        system_info = system_info.last()
    else:
        system_info = None

    real_days = 0
    rest_hours = 0
    total_production = 0
    total = 0
    payment_sum = 0
    production = WorkerProduction.objects.filter(worker=pk)
    attendance = WorkerAttendance.objects.filter(worker=pk)
    payment = WorkerPayment.objects.filter(worker=pk)

    if attendance:
        val = 0
        for item in attendance:
            if item.hour_count == 1:
                hours = 6
            elif item.hour_count == 2:
                hours = 8
            elif item.hour_count == 3:
                hours = 12
            elif item.hour_count == 4:
                hours = 18
            else:
                hours = 0
            val = val + hours
        count_days = val
        real_days = int(count_days / 12)
        rest_hours = int(count_days % 12)

        worker_price = worker.day_cost
        count_days = real_days
        count_hours = rest_hours / 12
        sum_price = count_days * worker_price
        sum_price2 = count_hours * worker_price
        total = sum_price + sum_price2

    if production:
        total = production.aggregate(quantity=Sum('quantity')).get('quantity')
        cost = production.aggregate(total=Sum('total')).get('total')
        # price = worker.day_cost
        # if price and total != None:
        #     cost = total * price
        # else:
        #     cost = 0
        total_production = total
        total = cost

    if payment:
        payment_sum = payment.aggregate(price=Sum('price')).get('price')

    context = {
        'system_info': system_info,
        'date': datetime.now(),
        'user': request.user.username,
        'worker': worker,
        'total_production': total_production,
        'total': total,
        'real_days': real_days,
        'rest_hours': rest_hours,
        'payment_sum': payment_sum,
    }
    html_string = render_to_string('Worker_Reports/print_worker_details.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/invoice_pdf.css')], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    return response



def WorkerPrice(request, pk):
    new_price = request.POST.get('new_price') or 0
    try:
        new_price = Decimal(new_price)
    except:
        new_price = Decimal(0)

    worker_quantity = WorkerProduction.objects.filter(worker__id=pk)
    worker_object = Worker.objects.get(id=pk)
    worker_object.day_cost = new_price
    worker_object.save()
    
    for x in worker_quantity:
        x.price = new_price
        x.total = x.quantity * new_price  # assuming quantity is numeric field
    WorkerProduction.objects.bulk_update(worker_quantity, ['price', 'total'])

    return redirect('Workers:WorkerDetails', pk=pk)