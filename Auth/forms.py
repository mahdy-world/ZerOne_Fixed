from django import forms
from .models import User

class ChangePasswordForm(forms.ModelForm):
    class Meta():
        model = User
        fields = ['password']
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'required':'required' }),
        }

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['password'].label = "كلمة المرور الجديدة"


class RegisterForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = [
            'username','password','first_name','last_name','is_active','is_superuser'
        ]
        
        widgets = {
            'password': forms.PasswordInput(attrs={'class':'form-control', 'name':'password' , 'placeholder':'ضع كلمة سر جديدة ....'}),
            'username': forms.TextInput(attrs={'class':'form-control','name':'username'}),
            'first_name': forms.TextInput(attrs={'class':'form-control','name':'first_name'}),
            'last_name': forms.TextInput(attrs={'class':'form-control','name':'last_name'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "اسم المستخدم" 
        self.fields['username'].help_text = "" 
        
        self.fields['password'].label = "كلمة المرور"

        instance = self.instance
        if instance.username:
            self.fields['password'].required = False
         
        self.fields['first_name'].label = "الاسم الاول"   
        self.fields['last_name'].label = " الاسم الاخير"  
         
         
        self.fields['is_active'].label = "نشط"   
        self.fields['is_active'].help_text = "يعمل / لا يعمل .... بديل للحذف" 
          
        self.fields['is_superuser'].label = "مسئول"   
        self.fields['is_superuser'].help_text = "لدية كل الصلاحيات (الحذف / التعديل)"
