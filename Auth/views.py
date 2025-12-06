from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import *
from django.urls import reverse_lazy
from django.contrib.auth.hashers import check_password
from .models import User
from Auth.forms import ChangePasswordForm, RegisterForm


# Create your views here.
class Login(View):
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('Core:index')
            else:
                error = 'تم ايقاف الحساب الخاص بك '
                return render(request, 'login.html', context={'error': error})
        else:
            if User.objects.filter(username=username):
                us = User.objects.get(username=username)
                if us.is_active == False:
                    error = 'تم ايقاف الحساب الخاص بك '
                else:
                    error = 'برجاء التأكد من اسم المستخدم وكلمة المرور'
            else:
                error = 'برجاء التأكد من اسم المستخدم وكلمة المرور'
            return render(request, 'login.html', context={'error': error})

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('Core:index')
        return render(request, 'login.html')


class Logout(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('Auth:login')


def ChangePassword(request):
    form = ChangePasswordForm(request.POST or None)
    action_url = reverse_lazy('Auth:ChangePassword')
    success_url = reverse_lazy('Core:index')

    password = form["password"].value()
    title = "تغير كلمة المرور"
    current_passowrd = request.user.password
    
    context = {
        'title':title,
        'message':'change',
        'form': form,
        'action_url' : action_url
    }
    
    if form.is_valid():
        old_password = request.POST.get('old_password')
        match_check = check_password(old_password,current_passowrd)
        if match_check:
            user = User.objects.get(username=request.user)
            user.set_password(password) 
            user.save()
            messages.success(request, " تم تغيير كلمة السر بنجاح", extra_tags="success")
            if request.POST.get('url'):
                return request.POST.get('url')
            else:
                return success_url
            # return redirect('Core:index')
        else:
            messages.success(request, " خطأ! كلمة السر القديمة غير صحيحة .. حاول مرة أخري", extra_tags="danger")
            if request.POST.get('url'):
                return request.POST.get('url')
            else:
                return success_url
            # return redirect('Core:index')
            
    return render(request,'forms/form_template.html', context)        


def create_user(request,):
    action_url = reverse_lazy('Auth:create_user')
    form = RegisterForm(request.POST or None)
    
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        form.save()
        messages.success(request, " تم اضافة مستخدم بنجاح", extra_tags="success")
        return redirect('Core:index')
    
    context = {
        'title': 'إضافة مستخدم جديد',
        'form': form,
        'action_url':action_url
    }
    return render(request, 'forms/user_form.html', context)


class Users(LoginRequiredMixin, ListView):
    login_url = '/auth/login/'
    model = User 
    template_name = 'users.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] =  'قائمة المستخدمين'
        return context
    

class UsersUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/auth/login/'
    model = User 
    template_name = 'forms/user_form.html'
    form_class = RegisterForm
    success_url = reverse_lazy('Core:index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'تعديل المستخدم  : ' + str(self.object)
        context['message'] = 'update'
        context['action_url'] = reverse_lazy('Auth:UsersUpdate', kwargs={'pk': self.object.id})
        return context
    
    def get_success_url(self):
        messages.success(self.request, "تم تعديل بيانات مستخدم بنجاح", extra_tags="success")
        if self.request.POST.get('url'):
            return self.request.POST.get('url')
        else:
            return self.success_url
        
        
    def form_valid(self, form):
        user_pass = form.cleaned_data.get("password").replace(" ", "")
        myform = User.objects.get(id=self.kwargs['pk'])
        myform.username = form.cleaned_data.get("username")
        myform.first_name = form.cleaned_data.get("first_name")
        myform.last_name = form.cleaned_data.get("last_name")
        myform.is_active = form.cleaned_data.get("is_active")
        myform.is_superuser = form.cleaned_data.get("is_superuser")
        if user_pass:
            myform.set_password(user_pass)
            myform.save(update_fields=['username', 'first_name', 'last_name' ,  'is_active', 'is_superuser', 'password'])
        else: 
            myform.save(update_fields=['username', 'first_name', 'last_name' ,  'is_active', 'is_superuser',])
        return redirect(self.get_success_url())