from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Admin'),
        (2, 'Staff'),
        (3, 'Customer'),
    )
    
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=3)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número debe estar en el formato: '+999999999'. Hasta 15 dígitos."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return self.username

    def is_admin(self):
        return self.user_type == 1 or self.is_superuser
    
    def is_staff_user(self):
        return self.user_type == 2 or self.is_staff
    
    def is_customer(self):
        return self.user_type == 3