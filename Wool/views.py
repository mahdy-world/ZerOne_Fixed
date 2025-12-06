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

# Create your views here.
class WoolList(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = Wool
    paginate_by = 12
    template_name = 'Wool/wool_list.html'

    def get_queryset(self):
        queryset = self.model.objects.all().order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'active'
        context['count'] = self.model.objects.all().count()
        context['wool_object_serach'] = self.model.objects.all()
        return context
    
class WoolCreate(LoginRequiredMixin, CreateView):
    login_url = '/auth/login/'
    model = Wool
    form_class = WoolForm
    template_name = 'forms/form_template.html'
    success_url = reverse_lazy('Wool:WoolList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'اضافة خامة جديدة'
        context['message'] = 'create'
        context['action_url'] = reverse_lazy('Wool:WoolCreate')
        return context

    def get_success_url(self):
        messages.success(self.request, "تم اضافة خامة جديدة", extra_tags="success")
        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url


class WoolUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Wool
    form_class = WoolForm
    template_name = 'forms/form_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل بيانات الخامة: ' + str(self.object)
        context['message'] = 'update'
        context['action_url'] = reverse_lazy('Wool:WoolUpdate', kwargs={'pk': self.object.id})
        return context

    def get_success_url(self, **kwargs):
        messages.success(self.request, "تم تعديل بيانات الخامة بنجاح", extra_tags="success")
        return reverse('Wool:WoolList')


class WoolSuperDelete(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = Wool
    form_class = WoolDeleteForm
    template_name = 'forms/form_template.html'

    def get_success_url(self):
        return reverse('Wool:WoolList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف الخامة : ' + str(self.object.wool_name) + 'بشكل نهائي'
        context['message'] = 'super_delete'
        context['action_url'] = reverse_lazy('Wool:WoolSuperDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف الخامة " + str(self.object.wool_name) + " نهائيا بنجاح ", extra_tags="success")
        my_form = Wool.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect(self.get_success_url())


def WoolDetails(request, pk):
    wool_object = Wool.objects.get(id=pk)
    wool_color_objects = WoolColor.objects.filter(wool__id=wool_object.id).values('color__color_name', 'color__color_hex_code').annotate(wcount=Sum('count'), qcount=Sum('weight'))
    quantity = WoolSupplierQuantity.objects.filter(wool=wool_object).order_by('-id')

    wool_color_filter = Color.objects.all()
    wool_objects_supplier = WoolSupplier.objects.all()
    # action_url = reverse_lazy('Wool:AddWoolSupplierQuantity', kwargs={'pk': supplier.id})
    system_info = SystemInformation.objects.all()
    if system_info.count() > 0:
        system_info = system_info.last()
    else:
        system_info = None

    # inside form
    inside_form = WoolQuantityForm()
    action_url = reverse_lazy('Wool:AddWoolQuantity', kwargs={'pk': wool_object.id})
    
    context = {
        'wool_color_objects':wool_color_objects, 
        'system_info': system_info,
        'date': datetime.now().date(),
        'wool_object': wool_object,
        'inside_form': inside_form,
        'action_url': action_url,
        'quantity': quantity,
        'wool_color_filter': wool_color_filter,
        'wool_objects_supplier': wool_objects_supplier
    }
    return render(request, 'Wool/wool_details.html', context)

def AddWoolQuantity(request, pk):
    wool_object = Wool.objects.get(id=pk)
    form = WoolQuantityForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.wool = wool_object
        obj.admin = request.user
        # filter woolcolor object based on data from user 
        wool_color_object = WoolColor.objects.filter(wool=wool_object, color=form.cleaned_data['wool_color'])
        # return just id's for woolcolor object using values_list method
        wool_color_object_id =  wool_color_object.values_list('id', flat=True)
        # check if found id's or not 
        if wool_color_object_id:
            # convert queryset to list 
            wool_color_object_id_list = list(wool_color_object_id)
            # get object using id 
            color_wool_id = WoolColor.objects.get(id=wool_color_object_id_list[0]) 
            # check if id not = none and update data for color 
            if color_wool_id != None:
                print(wool_color_object_id)
                color_wool_id.count += form.cleaned_data['wool_item_count']
                color_wool_id.weight += form.cleaned_data['wool_weight']
                color_wool_id.save()
        else:
            wool_color_object = WoolColor()
            wool_color_object.wool = wool_object
            wool_color_object.color = form.cleaned_data['wool_color']
            wool_color_object.count = form.cleaned_data['wool_item_count']
            wool_color_object.weight = form.cleaned_data['wool_weight']
            wool_color_object.save()
        
        obj.save()
        
        
        
        messages.success(request, " تم اضافة كمية جديدة بنجاح ", extra_tags="success")
    else:
        messages.error(request, " حدث خطأ أثناء اضافة الكمية ", extra_tags="danger")
    return redirect('Wool:WoolDetails', pk=wool_object.id)


def DelWoolQuantity(request, pk):
    quant = WoolSupplierQuantity.objects.get(id=pk)
    id = quant.wool.id
    # filter woolcolor object based on data from user 
    wool_color_object = WoolColor.objects.filter(wool=quant.wool, color=quant.wool_color)
    # return just id's for woolcolor object using values_list method
    wool_color_object_id =  wool_color_object.values_list('id', flat=True)
    # check if found id's or not 
    if wool_color_object_id:
        # convert queryset to list 
        wool_color_object_id_list = list(wool_color_object_id)
        # get object using id 
        color_wool_id = WoolColor.objects.get(id=wool_color_object_id_list[0]) 
        # check if id not = none and update data for color 
        if color_wool_id != None:
            # print(wool_color_object_id)
            if  color_wool_id.count >= quant.wool_item_count:
                color_wool_id.count -= quant.wool_item_count
                color_wool_id.weight -= quant.wool_weight
                color_wool_id.save()
            else:
                color_wool_id.delete()
    quant.delete()
    messages.success(request, " تم حذف كمية بنجاح ", extra_tags="success")
    return redirect('Wool:WoolDetails', pk=id)


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
        context['title'] = 'اضافة تاجر خيط'
        context['message'] = 'create'
        context['action_url'] = reverse_lazy('Wool:WoolSupplierCreate')
        return context

    def get_success_url(self):
        messages.success(self.request, "تم اضافة تاجر خيط جديد", extra_tags="success")
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
        context['title'] = 'تعديل بيانات تاجر خيط: ' + str(self.object)
        context['message'] = 'update'
        context['action_url'] = reverse_lazy('Wool:WoolSupplierUpdate', kwargs={'pk': self.object.id})
        return context

    def get_success_url(self, **kwargs):
        messages.success(self.request, "تم تعديل بيانات تاجر خيط بنجاح", extra_tags="success")
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
        context['title'] = 'حذف تاجر خيط: ' + str(self.object)
        context['message'] = 'delete'
        context['action_url'] = reverse_lazy('Wool:WoolSupplierDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف تاجر خيط " + str(self.object) + ' بنجاح ', extra_tags="danger")
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
        context['title'] = 'استرجاع تاجر خيط: ' + str(self.object)
        context['message'] = 'restore'
        context['action_url'] = reverse_lazy('Wool:WoolSupplierRestore', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم استرجاع تاجر خيط " + str(self.object) + ' بنجاح ', extra_tags="dark")
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
        context['title'] = 'حذف تاجر خيط : ' + str(self.object.id) + 'بشكل نهائي'
        context['message'] = 'super_delete'
        context['action_url'] = reverse_lazy('Wool:WoolSupplierSuperDelete', kwargs={'pk': self.object.id})
        return context

    def form_valid(self, form):
        messages.success(self.request, " تم حذف تاجر خيط " + str(self.object) + " نهائيا بنجاح ", extra_tags="success")
        my_form = WoolSupplier.objects.get(id=self.kwargs['pk'])
        my_form.delete()
        return redirect(self.get_success_url())


def WoolSupplierQuantityDetail(request, pk):
    supplier = WoolSupplier.objects.get(id=pk)
    quantity = WoolSupplierQuantity.objects.filter(supplier=supplier)
    wool_color = Color.objects.all()
    wool_objects = Wool.objects.all()
    form = WoolSupplierQuantityForm()

    action_url = reverse_lazy('Wool:AddWoolSupplierQuantity', kwargs={'pk': supplier.id})

    system_info = SystemInformation.objects.all()
    if system_info.count() > 0:
        system_info = system_info.last()
    else:
        system_info = None

    context = {
        'supplier': supplier,
        'quantity': quantity,
        'form': form,
        'action_url': action_url,
        'system_info': system_info,
        'date': datetime.now().date(),
        'wool_color_objects': wool_color,
        'wool_name': wool_objects
    }
    return render(request, 'WoolSupplier/supplier_qunatity.html', context)


def AddWoolSupplierQuantity(request, pk):
    supplier = WoolSupplier.objects.get(id=pk)
    form = WoolSupplierQuantityForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.supplier = supplier
        obj.admin = request.user
        # filter woolcolor object based on data from user 
        wool_color_object = WoolColor.objects.filter(wool=form.cleaned_data['wool'], color=form.cleaned_data['wool_color'])
        # return just id's for woolcolor object using values_list method
        wool_color_object_id =  wool_color_object.values_list('id', flat=True)
        # check if found id's or not 
        if wool_color_object_id:
            # convert queryset to list 
            wool_color_object_id_list = list(wool_color_object_id)
            # get object using id 
            color_wool_id = WoolColor.objects.get(id=wool_color_object_id_list[0]) 
            # check if id not = none and update data for color 
            if color_wool_id != None:
                print(wool_color_object_id)
                color_wool_id.count += form.cleaned_data['wool_item_count']
                color_wool_id.weight += form.cleaned_data['wool_weight']
                color_wool_id.save()
        else:
            wool_color_object = WoolColor()
            wool_color_object.wool = form.cleaned_data['wool']
            wool_color_object.color = form.cleaned_data['wool_color']
            wool_color_object.count = form.cleaned_data['wool_item_count']
            wool_color_object.weight = form.cleaned_data['wool_weight']
            wool_color_object.save()
        obj.save()
        
        
        messages.success(request, " تم اضافة كمية جديدة بنجاح ", extra_tags="success")
    else:
        messages.error(request, " حدث خطأ أثناء اضافة الكمية ", extra_tags="danger")
    return redirect('Wool:WoolSupplierQuantity', pk=supplier.id)


def DelWoolSupplierQuantity(request, pk):
    quant = WoolSupplierQuantity.objects.get(id=pk)
    id = quant.supplier.id
    # filter woolcolor object based on data from user 
    wool_color_object = WoolColor.objects.filter(wool=quant.wool, color=quant.wool_color)
    # return just id's for woolcolor object using values_list method
    wool_color_object_id =  wool_color_object.values_list('id', flat=True)
    # check if found id's or not 
    if wool_color_object_id:
        # convert queryset to list 
        wool_color_object_id_list = list(wool_color_object_id)
        # get object using id 
        color_wool_id = WoolColor.objects.get(id=wool_color_object_id_list[0]) 
        # check if id not = none and update data for color 
        if color_wool_id != None:
            # print(wool_color_object_id)
            if  color_wool_id.count >= quant.wool_item_count:
                color_wool_id.count -= quant.wool_item_count
                color_wool_id.weight -= quant.wool_weight
                color_wool_id.save()
            else:
                color_wool_id.delete()
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
    }
    html_string = render_to_string('WoolSupplier_Reports/print_supplier_details.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf(stylesheets=[weasyprint.CSS('static/assets/css/invoice_pdf.css')], presentational_hints=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    return response