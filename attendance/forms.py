from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
from django import forms
from .models import Company, Worker, CustomUser

CustomUser = get_user_model()

class CustomLoginForm(forms.Form):
    username_or_email = forms.CharField(max_length=256, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean_username_or_email(self):
        username_or_email = self.cleaned_data['username_or_email']
        if "@" in username_or_email:
            validate_email(username_or_email)
            data = {'email': username_or_email}
        else:
            data = {'username': username_or_email}
        try:
            get_user_model().objects.get(**data)
        except get_user_model().DoesNotExist:
            raise ValidationError(
                _('This {} does not exist'.format(list(data.keys())[0])))
        else:
            return username_or_email
class KioskCodeForm(forms.Form):
    kiosk_code = forms.CharField(max_length=8, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Kiosk Code','id': 'kiosk_code_'}))
    
class AddDataForm(forms.Form):
    firstname = forms.CharField(max_length=256, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Firstname'}))
    lastname =forms.CharField(max_length=256, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Lastname'}))
    company =forms.CharField(max_length=256, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Company'}))
    def clean_firstname(self):
        return self.cleaned_data['firstname']
    def clean_lastname(self):
        return self.cleaned_data['lastname']
    def clean_company(self):
        return self.cleaned_data['company']
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("This email address is already exists.")
        return email
    
class RegistrationChoiceForm(forms.Form):
    registration_choice = forms.ChoiceField(
        choices=[('company', 'Company Registration'), ('worker', 'Worker Registration')],
        widget=forms.RadioSelect
    )
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields

class RegisterCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address']  # Add company-specific fields here

class RegisterWorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['company','firstname', 'lastname',]  # Add worker-specific fields here  


class ForgetPasswordEmailCodeForm(forms.Form):
    username_or_email = forms.CharField(max_length=256,
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control',
                                                   'placeholder': 'Type your username or email'}))

    def clean_username_or_email(self):
        username_or_email = self.cleaned_data['username_or_email']
        data = {'username': username_or_email}

        if '@' in username_or_email:
            validate_email(username_or_email)
            data = {'email': username_or_email}
        try:
            get_user_model().objects.get(**data)
        except get_user_model().DoesNotExist:
            raise ValidationError(
                'There is no account with this {}'.format(list(data.keys())[0]))

        if not get_user_model().objects.get(**data).is_active:
            raise ValidationError(_('This account is not active.'))

        return data


class ChangePasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'New password'
            }
        ),
    )
    new_password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm password',
            }
        ),
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data['new_password1']
        password2 = self.cleaned_data['new_password2']

        if password1 and password2 and password1 != password2:
            raise ValidationError(_('Passwords are not match'))
        password_validation.validate_password(password2)
        return password2
