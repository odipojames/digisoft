from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.hashers import check_password


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=10, unique=True, validators=[
        MinLengthValidator(6, 'The field must contain at least 6 characters')
    ])
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    username = None
    USERNAME_FIELD = 'account_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']
    
    


class Cheque(models.Model):
    cheque_number = models.CharField(max_length=20)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='Active')  # 'Active' or 'Stopped'