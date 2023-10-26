from django.db import models
from django import forms
from django.contrib.auth.hashers import check_password

# Create your models here.

class SignUpModel(models.Model):
    username = models.CharField(max_length=30)
    email = models.EmailField(null=False)
    password = models.CharField(max_length=128,default='my_default_password')

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

def __str__(self):
        return self.username

class UserModel(models.Model):
    username = models.CharField(max_length=30)
    email = models.EmailField(null=False)
    password = models.CharField(max_length=128)

class LoginModel(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=128)