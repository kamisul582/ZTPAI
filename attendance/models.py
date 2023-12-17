from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from os import path


def get_profile_picture_filepath(instance, filename):
    filename = filename.split('.')[-1]
    return path.join('profile_images', '{}profile_image.{}'.format(instance.pk, filename))


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

class Company(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.TextField(_('name'), max_length=500, blank=True)
    address = models.TextField(_('address'), max_length=250, blank=True)
    
    def __str__(self):
        return f"{self.id} {self.user} -> {self.name} {self.address} {self.__class__}"
    
class Worker(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    firstname = models.TextField(_('firstname'), max_length=500, blank=True)
    lastname = models.TextField(_('lastname'), max_length=250, blank=True)
    kiosk_code = models.CharField(_('kiosk_code'), max_length=10, blank=True)
    def __str__(self):
        return f"{self.id} {self.user} -> {self.firstname} {self.lastname} {self.kiosk_code}  works in {self.company} {self.__class__}"
    #groups = models.ManyToManyField(
    #    Group,
    #    verbose_name=_('groups'),
    #    blank=True,
    #    help_text=_(
    #        'The groups this user belongs to. A user will get all permissions '
    #        'granted to each of their groups.'
    #    ),
    #    related_name='company_groups',
    #    related_query_name='company_group',
    #)
    #user_permissions = models.ManyToManyField(
    #    Permission,
    #    verbose_name=_('user permissions'),
    #    blank=True,
    #    help_text=_('Specific permissions for this user.'),
    #    related_name='company_user_permissions',
    #    related_query_name='company_user_permission',
    #)
    
class Worktime(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add = True, blank=True)
    punch_in = models.DateTimeField(blank=True)
    punch_out = models.DateTimeField(blank=True, null=True)
    total_time = models.DurationField(blank=True, null=True)