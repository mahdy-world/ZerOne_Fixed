from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import *
from .forms import *
from django.contrib import messages
import weasyprint
from django.template.loader import render_to_string
from .models import *
from Core.models import SystemInformation
from datetime import datetime
from django.http import HttpResponse
from django.db.models.aggregates import Sum


class TreasuryList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Treasury
    paginate_by = 12
    template_name = 'Treasury/treasury_list.html'
    
    def get_queryset(self):
        qureyset = self.model.objects.filter(deleted=False).order_by('-id')
        return qureyset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'list'
        context['title'] = 'قائمة الخزائن'
        context['icons'] = '<i class="fas fa-shapes"></i>'
        context['page'] = 'active'
        context['count'] = self.model.objects.filter(deleted=False).count()
        return context


class TreasuryTrachList(LoginRequiredMixin, ListView):
    login_url = '/auth/login'
    model = Treasury
    paginate_by = 12
    template_name = 'Treasury/treasury_list.html'
    
    def get_queryset(self):
        queyset = self.model.objects.filter(deleted=True).order_by('-id')
        return queyset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'trach'
        context['count'] = self.model.objects.filter(deleted=True).count()
        return context


class TreasuryCreate(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = Treasury
    form_class = TreasuryForm
    template_name = 'forms/form_template.html'
    success_url = reverse_lazy('Treasury:TreasuryList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'اضافة خزنة جديدة'
        context['message'] = 'add'
        context['action_url'] = reverse_lazy('Treasury:TreasuryCreate')
        return context
    
    # def post(self, request):
    #     if request.method == 'POST':
    #         form =self.form_class(request.POST or None)
    #         if form.is_valid():
    #             myform = form.save(commit=False)
    #             myform.treasury_user = request.user
    #             myform.save()
    #             return redirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, "تم اضافة خزنة جديدة بنجاح", extra_tags="success")

        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url
    

class TreasuryUpdate(LoginRequiredMixin ,UpdateView):
    login_url = '/auth/login/'
    model = Treasury
    form_class = TreasuryFormUpdate
    template_name = 'forms/form_template.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل الخزنة: ' + str(self.object)
        context['message'] = 'update'
        context['action_url'] = reverse_lazy('Treasury:TreasuryUpdate', kwargs={'pk': self.object.id})
        return context
    
    def get_success_url(self):
        messages.success(self.request,  "تم تعديل الخزنة " + str(self.object) + " بنجاح ", extra_tags="success")
        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url
                

class TreasuryDelete(LoginRequiredMixin ,UpdateView):
    login_url = '/auth/login/'
    model = Treasury
    form_class = TreasuryDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Treasury:TreasuryList')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'نقل الخزنة الي سلة المهملات: ' + str(self.object)
        context['message'] = 'delete'
        context['action_url'] = reverse_lazy('Treasury:TreasuryDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم نقل الخزنة " + str(self.object) + ' الي سلة المهملات بنجاح ' , extra_tags="success")
        myform = Treasury.objects.get(id=self.kwargs['pk'])
        myform.deleted = 1
        myform.save()
        return redirect(self.get_success_url())        


class TreasuryRestore(LoginRequiredMixin ,UpdateView):
    login_url = '/auth/login/'
    model = Treasury
    form_class = TreasuryDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Treasury:TreasuryList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'استرجاع الخزنة: ' + str(self.object)
        context['message'] = 'restore'
        context['action_url'] = reverse_lazy('Treasury:TreasuryRestore', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم ارجاع الخزنة " + str(self.object) + ' الي القائمة بنجاح ' , extra_tags="success")
        myform = Treasury.objects.get(id=self.kwargs['pk'])
        myform.deleted = 0
        myform.save()
        return redirect(self.get_success_url())
    

class TreasurySuperDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Treasury
    form_class = TreasuryDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Treasury:TreasuryTrachList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف الخزنة : ' + str(self.object)
        context['message'] = 'super_delete'
        context['action_url'] = reverse_lazy('Treasury:TreasurySuperDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, "تم حذف الخزنة " + str(self.object) + " نهائيا بنجاح ", extra_tags="success")
        my_form = Treasury.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect(self.get_success_url())


class TreasuryDetails(LoginRequiredMixin, DetailView):
    login_url = '/auth/login/'
    model = Treasury
    template_name = 'Treasury/treasury_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'list'
        context['treasury'] = self.object
        context['form'] = TreasuryOperationForm
        tr = TreasuryOperation.objects.filter(treasury=self.object)
        context['treasury_operation_obj'] = tr.order_by('-operation_date', '-id')
        context['last_op'] = tr.last()
        context['total_deposit'] = TreasuryOperation.objects.filter(operation_type=1, treasury=self.object).aggregate(sum=Sum('operation_value')).get('sum')
        context['total_withdrawals'] = TreasuryOperation.objects.filter(operation_type=2, treasury=self.object).aggregate(sum=Sum('operation_value')).get('sum')

        return context


class TreasuryOperationDiv(LoginRequiredMixin, DetailView):
    login_url = '/auth/login/'
    model = Treasury
    template_name = 'Treasury/treasury_operation_div.html'

    def get_context_data(self, **kwargs):
        query_set = TreasuryOperation.objects.filter(treasury=self.object).order_by('-operation_date', '-id')
        date_val = self.request.GET.get('date_val')
        type_val = self.request.GET.get('type_val')

        if date_val:
            query_set = query_set.filter(operation_date=date_val)

        if type_val:
            query_set = query_set.filter(operation_type=int(type_val))

        context = super().get_context_data(**kwargs)
        context['type'] = 'list'
        context['treasury'] = self.object
        context['form'] = TreasuryOperationForm
        context['treasury_operation_obj'] = query_set
        context['last_op'] = TreasuryOperation.objects.filter(treasury=self.object).last()
        return context


class OperationInCreate(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = TreasuryOperation
    form_class = TreasuryOperationForm
    template_name = 'forms/form_template.html'

    def get_form_kwargs(self):
        kwargs = super(OperationInCreate, self).get_form_kwargs()
        kwargs['treasury_id'] = self.kwargs['pk']
        return kwargs

    def get_success_url(self):
        messages.success(self.request, "تم اضافة رصيد بنجاح", extra_tags="success")
        return reverse_lazy('Treasury:TreasuryDetails', kwargs={'pk': self.kwargs['pk']})
          
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'اضافة رصيد'
        context['message'] = 'add'
        context['action_url'] = reverse_lazy('Treasury:OperationInCreate',  kwargs={'pk': self.kwargs['pk']})
        return context
    
    def form_valid(self, form):
        form.save()
        obj = form.save(commit=False)
        myform = TreasuryOperation.objects.get(id=obj.id)
        myform.operation_user = self.request.user
        myform.treasury = Treasury.objects.get(id=self.kwargs['pk'])
        myform.operation_type = 1
        myform.save()

        myform2 = myform.treasury
        myform2.balance += myform.operation_value
        myform2.save(update_fields=['balance'])
        
        return redirect(self.get_success_url())


class OperationOutCreate(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = TreasuryOperation
    form_class = TreasuryOperationForm
    template_name = 'forms/form_template.html'

    def get_form_kwargs(self):
        kwargs = super(OperationOutCreate, self).get_form_kwargs()
        kwargs['treasury_id'] = self.kwargs['pk']
        return kwargs

    def get_success_url(self):
        messages.success(self.request, "تم سحب رصيد بنجاح", extra_tags="success")
        return reverse_lazy('Treasury:TreasuryDetails', kwargs={'pk': self.kwargs['pk']})
          
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'سحب رصيد'
        context['message'] = 'add'
        context['action_url'] = reverse_lazy('Treasury:OperationOutCreate', kwargs={'pk': self.kwargs['pk']})
        return context
    
    def form_valid(self, form):
        treasury = Treasury.objects.get(id=self.kwargs['pk'])
        operation_value = form.cleaned_data.get("operation_value")
        if operation_value > treasury.balance:
            messages.error(self.request, "خطأ! القيمة التي تريد سحبها أكبر من رصيد الخزنة", extra_tags="danger")
            return redirect('Treasury:TreasuryDetails', pk=self.kwargs['pk'])
        else:
            form.save()
            obj = form.save(commit=False)
            myform = TreasuryOperation.objects.get(id=obj.id)
            myform.operation_user = self.request.user
            myform.treasury = treasury
            myform.operation_type = 2
            myform.save()

            myform2 = myform.treasury
            myform2.balance -= myform.operation_value
            myform2.save(update_fields=['balance'])

            return redirect(self.get_success_url())
    

class OperationSuperDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = TreasuryOperation
    form_class = TreasuryOperationDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse_lazy('Treasury:TreasuryDetails', kwargs={'pk': self.object.treasury.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف العملية : ' + str(self.object)
        context['message'] = 'super_deletee'
        context['action_url'] = reverse_lazy('Treasury:OperationSuperDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        my_form = TreasuryOperation.objects.get(id=self.kwargs['pk'])

        treasury = Treasury.objects.get(id=my_form.treasury.id)
        if my_form.operation_type == 1:
            if my_form.operation_value > treasury.balance:
                messages.error(self.request, "خطأ! القيمة التي تريد خصمها أكبر من رصيد الخزنة", extra_tags="danger")
                return redirect('Treasury:TreasuryDetails', pk=treasury.id)
            else:
                treasury.balance -= my_form.operation_value
                messages.success(self.request, "تم حذف العملية وخصم قيمة العملية من رصيد الخزنة بنجاح", extra_tags="success")
        if my_form.operation_type == 2:
            treasury.balance += my_form.operation_value
            messages.success(self.request, "تم حذف العملية وارجاع قيمة العملية الي رصيد الخزنة بنجاح", extra_tags="success")
        treasury.save(update_fields=['balance'])

        my_form.delete()
        return redirect(self.get_success_url())


def TreasuryReport(request, pk):
    treasury = Treasury.objects.get(id=pk)
    treasury_operations = TreasuryOperation.objects.filter(treasury=treasury)
    treasury_operations_in = treasury_operations.filter(operation_type=1).aggregate(sum=Sum('operation_value')).get('sum')
    treasury_operations_out = treasury_operations.filter(operation_type=2).aggregate(sum=Sum('operation_value')).get('sum')

    system_info = SystemInformation.objects.all()
    if system_info.count() > 0:
        system_info = system_info.last()
    else:
        system_info = None

    context = {
        'system_info': system_info,
        'date': datetime.now(),
        'user': request.user.username,
        'treasury': treasury,
        'treasury_operations_in': treasury_operations_in,
        'treasury_operations_out': treasury_operations_out,
    }
    html_string = render_to_string('Treasury/treasury_report.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/invoice_pdf.css')], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    return response