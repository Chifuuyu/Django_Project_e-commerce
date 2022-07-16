import datetime

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm

from .models import *


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


class orderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_date', 'status']
