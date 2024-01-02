from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from os import path




class CustomUser(AbstractUser):
    is_worker = models.BooleanField(default = False)
    is_company = models.BooleanField(default = False)
    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='customuser_groups',
        related_query_name='customuser_group',)
    def save(self, *args, **kwargs):
        # Ensure that a user can only be a worker or a company, not both
        if self.is_worker:
            self.is_company = False
        elif self.is_company:
            self.is_worker = False

        super().save(*args, **kwargs)

class Company(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.TextField(_('name'), max_length=500, blank=True)
    address = models.TextField(_('address'), max_length=250, blank=True)
    
    def __str__(self):
        return f"{self.id} {self.user} -> {self.name} {self.address} {self.__class__}"

@receiver(post_save, sender=CustomUser)
def create_or_update_company(sender, instance, created, **kwargs):
    if created and instance.is_company:
        Company.objects.create(user=instance)
    elif not created and instance.is_company:
        instance.company.save()

class Worker(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    firstname = models.TextField(_('firstname'), max_length=500, blank=True)
    lastname = models.TextField(_('lastname'), max_length=255, blank=True)
    kiosk_code = models.CharField(_('kiosk_code'), max_length=10, blank=True)
    def __str__(self):
        return f"{self.id} {self.user} -> {self.firstname} {self.lastname} {self.kiosk_code}  works in {self.company} {self.__class__}"


    
class Worktime(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add = True, blank=True)
    punch_in = models.DateTimeField(blank=True)
    punch_out = models.DateTimeField(blank=True, null=True)
    total_time = models.DurationField(blank=True, null=True)