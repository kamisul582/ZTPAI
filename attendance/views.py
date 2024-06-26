import json
from django.utils import timezone
import random
import string
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from .forms import (
    CustomLoginForm,
    ChangePasswordForm,
    KioskCodeForm,
    RegisterCompanyForm,
    RegisterWorkerForm,
    RegistrationChoiceForm,
    AddSubordinateForm,
    CustomUserCreationForm
)
from .models import CustomUser, Worktime, Company, Worker
from .decorators import only_authenticated_user, redirect_authenticated_user
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from formtools.wizard.views import SessionWizardView
from rest_framework.decorators import api_view
from django.core.serializers import serialize
from django.db.models import Q
from datetime import timedelta
from django.conf import settings

EMAIL_ACTIVATION = getattr(settings, "EMAIL_ACTIVATION", True)

@only_authenticated_user
def home_view(request):
    print(request)
    user_id = request.user.id
    user = get_object_or_404(CustomUser, id=user_id)
    if user.is_worker:
        try:
            worker = Worker.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            return render(request, 'attendance/home.html', {'users': user, 'user_id': user_id,'error':'Worker not found'})
        worktime_entries = Worktime.objects.filter(worker=worker)
        return render(request, 'attendance/home.html',
                      {'users': user, 'user_id': user_id, 'worker': worker, 'worktime_entries': worktime_entries})
    if user.is_company:
        try:
            company = Company.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            return render(request, 'attendance/home.html', {'users': user,'error':'Company not found'})
        form = KioskCodeForm()
        return render(request, 'attendance/home.html', {'users': user, 'company': company, 'user_id': user_id, 'form': form})
    return redirect('attendance:logout')

@only_authenticated_user
def get_worker_worktime(request, user_id):
    requesting_user_id = request.user.id
    requesting_user = get_object_or_404(CustomUser, id=requesting_user_id)
    employed_users = [worker.user.id for worker in get_employed_worker_ids(request)]
    if user_id not in employed_users:
        return redirect('attendance:get_employees')
    try:
        worker = Worker.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        return render(request, 'attendance/employee_worktime.html', {'users': requesting_user, 'user_id': user_id})
    worktime_entries = Worktime.objects.filter(worker=worker)
    return render(request, 'attendance/employee_worktime.html', 
                  {'user': requesting_user, 'worker': worker, 'worktime_entries': worktime_entries})


def get_company_from_user(user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if not user.is_company:
        print("user is not company", user.is_company)
        return None
    return Company.objects.get(user_id=user_id)


def get_worker_from_user(user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if not user.is_worker:
        print("user is not worker", user.is_company)
        return None
    return Worker.objects.get(user_id=user_id)

def build_filter_q(request, filter_fields):
    filter_q = Q()
    filter_values = {}

    for field in filter_fields:
        filter_value = request.GET.get(field, '')
        lookup = 'exact' if field == 'user' else 'icontains'

        if filter_value:
            filter_q &= Q(**{f'{field}__{lookup}': filter_value})
        filter_values[field] = filter_value

    return filter_q, filter_values

@only_authenticated_user
def add_subordinates(request):
    if not request.user.is_manager:
        return redirect('attendance:home')
    manager = get_worker_from_user(request.user.id)
    if request.method == 'POST':
        form = AddSubordinateForm(request.POST,company=manager.company)
        if form.is_valid():
            subordinates = form.cleaned_data['subordinates']
            for subordinate in subordinates:
                subordinate.manager = manager
                subordinate.save()
            print("subordinates",subordinates)
            print("manager.subordinate.all()",manager.subordinate.all())
            print("Worker.objects.filter(manager=manager)",Worker.objects.filter(manager=manager))

            return redirect('attendance:home')
    else:
        form = AddSubordinateForm(company=manager.company)
    return render(request, 'attendance/add_subordinates.html', {'form': form, 'manager': manager})

@only_authenticated_user
def get_employees(request, sort='user_id', filter=''):
    company = get_company_from_user(request.user.id)
    if not company and not request.user.is_manager:
        return JsonResponse({'error': 'User is not associated with a company'})
    sort_param = request.GET.get('sort', 'user_id')
    filter_fields = ['user', 'firstname', 'lastname', 'kiosk_code']
    filter_q, filter_values = build_filter_q(request, filter_fields)
    if company:
        combined_filter = Q(company=company) & filter_q
    if request.user.is_manager:
        manager = get_worker_from_user(request.user.id)
        combined_filter = Q(company=manager.company) & Q(manager=manager) & filter_q
    workers = json.loads(serialize("json", Worker.objects.filter(combined_filter).order_by(sort_param)))
    if 'clear_filters' in request.GET:
        return redirect('attendance:get_employees')

    context = {
        'workers': workers,
        'current_sort': sort_param,
        'filter_values': filter_values.items(),
        'filter_fields': filter_fields,
        'company': company
    }

    return render(request, 'attendance/employees.html', context)

def get_user_ids(request):
    workers = Worker.objects.all().values('user_id', 'firstname','lastname')
    print(workers)
    return JsonResponse({'workers': list(workers)})

def get_employed_user_ids_json(request):
    
    company = get_company_from_user(request.user.id)
    if company:
        print("company",company)
        workers = Worker.objects.all().values('user_id', 'firstname','lastname')
    if request.user.is_manager:
        manager = get_worker_from_user(request.user.id)
        print("manager",manager)
        workers = Worker.objects.filter(manager=manager).values('user_id', 'firstname','lastname')
    print(workers)
    return JsonResponse({'workers': list(workers)})

def get_employed_worker_ids(request):
    company = get_company_from_user(request.user.id)
    if company:
        workers = Worker.objects.filter(company=company)
    if request.user.is_manager:
        manager = get_worker_from_user(request.user.id)
        workers = Worker.objects.filter(manager=manager)
    if request.user.is_worker and not request.user.is_manager:
        workers = [get_worker_from_user(request.user.id)]
    return workers

@login_required
@api_view(['POST'])
def add_worktime(request, worker=None):
    print("adding worktime")
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if worker is None:
            worker = get_worker_from_user(user_id)
        existing_entry = Worktime.objects.filter(worker=worker, punch_out__isnull=True).first()
        if existing_entry:
            existing_entry.punch_out = timezone.now()
            existing_entry.total_time = existing_entry.punch_out - existing_entry.punch_in
            existing_entry.total_time = timedelta(seconds=round(existing_entry.total_time.total_seconds()))
            existing_entry.save()
            return JsonResponse({'status': 'success'})
        new_entry = Worktime(worker=worker, punch_in=timezone.now(), date=timezone.now().date())
        new_entry.save()
        return JsonResponse({'status': 'success', 'entry_id': new_entry.id})


@api_view(['GET'])
def get_worktime_details(request,entry_id):
    worktime = get_object_or_404(Worktime, id=entry_id)
    data = {
        'date': worktime.date,
        'punch_in': worktime.punch_in,
        'punch_out': worktime.punch_out,
        'total_time': worktime.total_time,
    }
    return JsonResponse(data)


@login_required
def update_worktime_by_kiosk_code(request):
    print("Updating worktime by kiosk code")
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        form = KioskCodeForm(request.POST)
        if form.is_valid():
            company = Company.objects.get(user_id=user_id)
            kiosk_code = form.cleaned_data['kiosk_code']
            try:
                worker = Worker.objects.get(company=company, kiosk_code=kiosk_code)
            except ObjectDoesNotExist:
                return JsonResponse({'status': 'failure', 'message': "Worker with that Kiosk Code was not found."})
            response = add_worktime(request, worker)
            response_data = response.content.decode("UTF-8")
            worker_info = f"{worker.firstname} {worker.lastname}"
            if 'entry_id' in response_data:
                return JsonResponse({'status': 'success', 'message':
                                     "Successfully created a new worktime entry for: ", 'worker': worker_info})
            return JsonResponse({'status': 'success', 'message':
                                 "Successfully updated an existing worktime entry for: ", 'worker': worker_info})
    else:
        form = KioskCodeForm()
    return render(request, 'attendance/home.html', {'form': form})


@redirect_authenticated_user
@api_view(['POST', 'GET'])
def login_view(request):
    error = None
    if request.method != 'POST':
        form = CustomLoginForm()
        return render(request, 'attendance/login.html', {'form': form, 'error': error})
    form = CustomLoginForm(request.POST)
    if not form.is_valid():
        error = 'Invalid Credentials'
        return render(request, 'attendance/login.html', {'form': form, 'error': error})
    user = authenticate(
        request, username=form.cleaned_data['username_or_email'], password=form.cleaned_data['password'])
    if user:
        if user.is_active:
            login(request, user)
            return redirect('attendance:home')
        activateEmail(request, user, user.email)
        error = f'Account is not active. Activation email was sent to {user.email}' 
        return render(request, 'attendance/login.html', {'form': form, 'error': error})
    error = 'Invalid Credentials'
    return render(request, 'attendance/login.html', {'form': form, 'error': error})


@only_authenticated_user
@login_required
def logout_view(request):
    logout(request)
    return redirect('attendance:login')

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp)  + str(user.is_active)
        )
account_activation_token = AccountActivationTokenGenerator()

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        print("success")
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('attendance:login')
    else:
        messages.error(request, 'Activation link is invalid!')
        print("user",user,"token check",account_activation_token.check_token(user, token),"token",token)
        return render(request,'attendance/invalid_token.html')
    
def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('attendance/template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    print(email.subject,email.body,email.to)
    if email.send():
        print("worked")
    return JsonResponse({'status': 'success', 'message':
                                 f'Dear <b>{user}</b>, please go to your email <b>{to_email}</b> inbox and click on \
                                    received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.'})
    
STEP_ONE = u'0'
STEP_TWO = u'1'
STEP_THREE = u'2'
STEP_FOUR = u'3'


class MyWizard(SessionWizardView):
    @staticmethod
    def return_true(wizard):
        return True

    @staticmethod
    def check_step(wizard, valid_choices):
        step_1_info = wizard.get_cleaned_data_for_step(STEP_ONE)
        return step_1_info and step_1_info['registration_choice'] in valid_choices

    condition_dict = {
        STEP_ONE: lambda wizard: True,
        STEP_TWO: lambda wizard: True,
        STEP_THREE: lambda wizard: MyWizard.check_step(wizard, ['company']),
        STEP_FOUR: lambda wizard: MyWizard.check_step(wizard, ['worker', 'manager']),
    }

    form_list = [
        (STEP_ONE, RegistrationChoiceForm),
        (STEP_TWO, CustomUserCreationForm),
        (STEP_THREE, RegisterCompanyForm),
        (STEP_FOUR, RegisterWorkerForm),
    ]


class RegistrationWizardView(MyWizard):
    template_name = 'attendance/wizard_form.html'

    def done(self, form_list, **kwargs):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        return self.create_user(data)
    def create_user(self, data):
        user = CustomUser.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password1']
        )
        user.is_active = False
        if data['registration_choice'] == 'company':
            return self.create_company(user,data)
        elif data['registration_choice'] == 'worker' or data['registration_choice'] == 'manager':
            return self.create_worker(user,data)
        else:
            return render(self.request, 'attendance/registration_error.html')
    def create_company(self,user,data):
        Company.objects.create(
                user=user,
                name=data['name'],
                address=data['address']
            )
        user.is_company = True
        user.save()
        if EMAIL_ACTIVATION:
            activateEmail(self.request, user, data['email'])
        return redirect('attendance:login')
    def create_worker(self,user,data):
        Worker.objects.create(
                user=user,
                company=data['company'],
                firstname=data['firstname'],
                lastname=data['lastname'],
                kiosk_code=generate_kiosk_codes(company=data['company'])[0]
            )
        user.is_worker = True
        if data['registration_choice'] == 'manager':
            user.is_manager = True
        user.save()
        if EMAIL_ACTIVATION:
            activateEmail(self.request, user, data['email'])
        return redirect('attendance:login')

def generate_kiosk_codes(company,amount = 1):
    workers = Worker.objects.filter(company=company)
    valid_codes = []
    used_codes = [worker.kiosk_code for worker in workers]
    i = 0
    while i < 1000 and len(valid_codes) < amount:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code in used_codes:
            i += 1
        else:
            valid_codes.append(code)
            used_codes.append(code)
    return valid_codes

#@redirect_authenticated_user
#@api_view(['POST'])
def reset_new_password_view(request):

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = CustomUser.objects.get(email=email)
            user.password = make_password(form.cleaned_data["new_password2"])
            user.save()
            return redirect('attendance:login')
    else:
        form = ChangePasswordForm()
    return render(request, 'attendance/new_password.html', {'form': form})
