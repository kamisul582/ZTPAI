import json
from django.utils import timezone
import random
import string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.shortcuts import redirect, render

from django.contrib.auth.decorators import login_required
from attendance.admin import CustomUserCreationForm
from .forms import (
    CustomLoginForm,
    ChangePasswordForm,
    KioskCodeForm,
    RegisterCompanyForm,
    RegisterWorkerForm,
    RegistrationChoiceForm,
)
from .models import CustomUser, Worktime, Company, Worker
from .decorators import only_authenticated_user, redirect_authenticated_user
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from formtools.wizard.views import SessionWizardView
from rest_framework.decorators import api_view
from django.core.serializers import serialize
from django.db.models import Q


@only_authenticated_user
def home_view(request):
    user = CustomUser.objects.filter(username=request.user.username)
    user_id = request.user.id
    user = get_object_or_404(CustomUser, id=user_id)
    if user.is_worker:
        try:
            worker = Worker.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            return render(request, 'attendance/home.html', {'users': user, 'user_id': user_id})

        worktime_entries = Worktime.objects.filter(worker=worker)
        return render(request, 'attendance/home.html',
                      {'users': user, 'user_id': user_id, 'worker': worker, 'worktime_entries': worktime_entries})

    if user.is_company:
        company = Company.objects.get(user_id=user_id)
        form = KioskCodeForm()
        return render(request, 'attendance/home.html', {'users': user, 'company': company, 'user_id': user_id, 'form': form})

@only_authenticated_user
def get_worker_worktime(request, user_id):
    print("Getting employee worktime")
    company_user_id = request.user.id
    company_user = get_object_or_404(CustomUser, id=company_user_id)
    try:
        worker = Worker.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        return render(request, 'attendance/employee_worktime.html', {'users': company_user, 'user_id': user_id})
    worktime_entries = Worktime.objects.filter(worker=worker)
    return render(request, 'attendance/employee_worktime.html', {'user': company_user, 'worker': worker, 'worktime_entries': worktime_entries})


@only_authenticated_user
# @api_view(['GET'])
def get_employees(request,sort='user_id', filter=''):
    print("Getting employees")
    user = CustomUser.objects.filter(username=request.user.username)
    user_id = request.user.id
    user = get_object_or_404(CustomUser, id=user_id)
    if not user.is_company:
        print("user is not company", user.is_company)
        return
    company = Company.objects.get(user_id=user_id)
    sort_param = request.GET.get('sort', 'user_id')
    filter_fields = ['user','firstname', 'lastname', 'kiosk_code']
    filter_q = Q()
    for field in filter_fields:
        filter_value = request.GET.get(field, '')
        if filter_value:
            filter_q &= Q(**{f'{field}__icontains': filter_value})
    
    fixed_filter_condition = Q(company=company) 
    combined_filter = fixed_filter_condition & filter_q
    print(combined_filter)
    print(request.GET)
    workers = Worker.objects.filter(combined_filter).order_by(sort_param)
    workers = serialize("json", workers)
    workers = json.loads(workers)
    context = {
        'workers': workers,
        'current_sort': sort_param,
        'filter_values': {field: request.GET.get(field, '') for field in filter_fields},
        'filter_fields': filter_fields,
        'company': company
    }
    return render(request, 'attendance/employees.html', context)
        # return JsonResponse(workers, safe=False, status=200)


@login_required
@api_view(['POST'])
def add_worktime(request, worker=None):
    print("Adding worktime")
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if worker is None:
            worker = Worker.objects.get(user_id=user_id)

        # Check if there is an existing entry for the user and current date
        existing_entry = Worktime.objects.filter(worker=worker, punch_out__isnull=True).first()

        if existing_entry:
            # Update the existing entry with punch_out time
            existing_entry.punch_out = timezone.now()
            existing_entry.total_time = existing_entry.punch_out - existing_entry.punch_in
            existing_entry.save()
        else:
            # Create a new entry with punch_in time
            new_entry = Worktime(worker=worker, punch_in=timezone.now(), date=timezone.now().date())
            new_entry.save()
            return JsonResponse({'status': 'success', 'entry_id': new_entry.id})
        return JsonResponse({'status': 'success'})


@api_view(['GET'])
def get_worktime_details(request, entry_id):
    worktime = get_object_or_404(Worktime, id=entry_id)
    data = {
        'date': worktime.date,
        'punch_in': worktime.punch_in,
        'punch_out': worktime.punch_out,
        'total_time': worktime.total_time,
    }
    return JsonResponse(data)


@login_required
# @api_view(['POST'])
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
                print("user not found")
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
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request, username=form.cleaned_data['username_or_email'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect('attendance:home')
            else:
                error = 'Invalid Credentials'
    else:
        form = CustomLoginForm()
    return render(request, 'attendance/login.html', {'form': form, 'error': error})


@only_authenticated_user
@login_required
def logout_view(request):
    logout(request)
    return redirect('attendance:login')


STEP_ONE = u'0'
STEP_TWO = u'1'
STEP_THREE = u'2'
STEP_FOUR = u'3'


class MyWizard(SessionWizardView):

    def return_true(wizard):
        return True

    def check_step_two(wizard):
        step_1_info = wizard.get_cleaned_data_for_step(STEP_ONE)
        # Do something with info; can retrieve for any prior steps
        if step_1_info:
            if step_1_info['registration_choice'] == 'company':
                print("step_1_info", step_1_info)
                return True
            else:
                return False

    def check_step_three(wizard):
        step_1_info = wizard.get_cleaned_data_for_step(STEP_ONE)
        if step_1_info:
            if step_1_info['registration_choice'] == 'worker':
                print("step_1_info", step_1_info)
                return True
            else:
                return False

    condition_dict = {
        STEP_ONE: return_true,
        STEP_TWO: return_true,
        STEP_THREE: check_step_two,
        STEP_FOUR: check_step_three,
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

        user = CustomUser.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password1']
        )

        if data['registration_choice'] == 'company':
            Company.objects.create(
                user=user,
                name=data['name'],
                address=data['address']
            )
            user.is_company = True
            user.save()
            return redirect('attendance:login')
        elif data['registration_choice'] == 'worker':

            Worker.objects.create(
                user=user,
                company=data['company'],
                firstname=data['firstname'],
                lastname=data['lastname'],
                kiosk_code=generate_kiosk_code(company=data['company'])
            )
            user.is_worker = True
            user.save()
            return redirect('attendance:login')
        else:
            return render(self.request, 'attendance/registration_error.html')


def generate_kiosk_code(company):
    workers = Worker.objects.filter(company=company)
    print("workers", workers)
    codes = []
    i = 0
    while i < 20:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        for worker in workers:
            codes.append(worker.kiosk_code)
        print("codes", codes)
        if code in codes:
            i += 1
        else:
            return code


@redirect_authenticated_user
@api_view(['POST'])
def reset_new_password_view(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            email = request.session['email']
            del request.session['email']
            user = CustomUser.objects.get(email=email)
            user.password = make_password(form.cleaned_data["new_password2"])
            user.save()
            messages.success(request, _(
                "Your password changed. Now you can login with your new password."))
            return redirect('attendance:login')
    else:
        form = ChangePasswordForm()
    return render(request, 'attendance/new_password.html', {'form': form})
