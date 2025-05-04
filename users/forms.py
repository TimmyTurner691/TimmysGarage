from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .models import CustomUser
import re

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'phone_number', 'birth_date')
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        
        # Validaciones de seguridad para la contraseña
        if len(password2) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        if not re.search(r'[A-Z]', password2):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
            
        if not re.search(r'[a-z]', password2):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
            
        if not re.search(r'[0-9]', password2):
            raise ValidationError("La contraseña debe contener al menos un número.")
            
        if not re.search(r'[^A-Za-z0-9]', password2):
            raise ValidationError("La contraseña debe contener al menos un carácter especial.")
            
        return password2

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'birth_date', 'address')

class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        
        # Reutilizar las mismas validaciones que en el formulario de creación
        if len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
            
        if not re.search(r'[a-z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
            
        if not re.search(r'[0-9]', password1):
            raise ValidationError("La contraseña debe contener al menos un número.")
            
        if not re.search(r'[^A-Za-z0-9]', password1):
            raise ValidationError("La contraseña debe contener al menos un carácter especial.")
            
        return password1