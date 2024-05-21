from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
from django import forms
from .models import Company, Worker, CustomUser


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
        attrs={'class': 'form-control', 'placeholder': 'Kiosk Code', 'id': 'kiosk_code_'}))



class RegistrationChoiceForm(forms.Form):
    registration_choice = forms.ChoiceField(
        choices=[('company', 'Company Registration'), ('worker', 'Worker Registration'), ('manager','Manager Registration')],
        widget=forms.RadioSelect
    )


#class CustomUserCreationForm(UserCreationForm):
#    class Meta:
#        model = CustomUser
#        fields = UserCreationForm.Meta.fields
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email',)

class RegisterCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'custom-class-for-name'}),
            'address': forms.Textarea(attrs={'class': 'custom-class-for-address', 'rows': 3}),
        }

class AddSubordinateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company')
        super(AddSubordinateForm, self).__init__(*args, **kwargs)
        self.fields['subordinates'].queryset = Worker.objects.filter(company=company)

    subordinates = forms.ModelMultipleChoiceField(queryset=Worker.objects.none(), widget=forms.CheckboxSelectMultiple)

class RegisterWorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['company', 'firstname', 'lastname',]
        widgets = {
            'firstname': forms.TextInput(attrs={'class': 'custom-class-for-name'}),
            'lastname': forms.TextInput(attrs={'class': 'custom-class-for-lastname'}),
        }
#class RegisterWorkerForm(forms.Form):
#    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=True)
#    firstname = forms.CharField(max_length=100, required=True)
#    lastname = forms.CharField(max_length=100, required=True)
    
class FileUploadForm(forms.Form):
    file = forms.FileField()

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
    email = forms.CharField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }
        ),
    )
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
