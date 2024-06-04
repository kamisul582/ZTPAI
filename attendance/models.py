from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save


class CustomUser(AbstractUser):
    is_worker = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    password_change_required = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_worker:
            self.is_company = False
        elif self.is_company:
            self.is_worker = False
            self.is_manager = False
        super().save(*args, **kwargs)

class Company(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.TextField(_('name'), max_length=500, blank=True)
    address = models.TextField(_('address'), max_length=250, blank=True)

    def __str__(self):
        return f"{self.id} {self.user} {self.name} {self.address}"

class Worker(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    firstname = models.TextField(_('firstname'), max_length=500, blank=True)
    lastname = models.TextField(_('lastname'), max_length=255, blank=True)
    kiosk_code = models.CharField(_('kiosk_code'), max_length=10, blank=True)
    manager = models.ForeignKey('self', related_name='subordinate', on_delete=models.SET_NULL, blank=True, null=True)
    is_activated = models.BooleanField(default=False)

    def __str__(self):
        return f"""{self.id}. {self.firstname} {self.lastname}"""

class Worktime(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, blank=True)
    punch_in = models.DateTimeField(blank=True)
    punch_out = models.DateTimeField(blank=True, null=True)
    total_time = models.DurationField(blank=True, null=True)
