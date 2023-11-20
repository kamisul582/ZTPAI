from typing import Any
from django.db import models

class Company(models.Model):
    def __str__(self) -> str:
        return self.email + " " + self.company_name
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    company_address = models.CharField(max_length=200)

class User(models.Model):
   
    def __str__(self) -> str:
        return self.email + " " + self.name + " " + self.surname + " " + self.kiosk_code
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    employer  = models.ForeignKey(Company, on_delete=models.CASCADE)
    kiosk_code = models.CharField(max_length=10)

class WorkTime(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add = True, blank=True)
    punch_in = models.DateField(blank=True)
    punch_out = models.DateField(blank=True)
    total_time = models.DateField(blank=True)
# Create your models here.
