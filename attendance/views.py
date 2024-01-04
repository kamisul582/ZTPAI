from django.utils import timezone
import random
import string
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.shortcuts import (
    redirect,
    render,
)
from django.contrib.auth.decorators import login_required
from django.views import View

from attendance.admin import CustomUserCreationForm

from .forms import (
    CustomLoginForm,
    #RegisterForm,
    ForgetPasswordEmailCodeForm,
    ChangePasswordForm,
    KioskCodeForm,
    RegisterCompanyForm,
    RegisterWorkerForm,
    RegistrationChoiceForm,
)
from .models import CustomUser, Worktime, Company, Worker
from .utils import (
    send_activation_code,
    send_reset_password_code,
)
from .decorators import only_authenticated_user, redirect_authenticated_user
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from formtools.wizard.views import SessionWizardView
from django.urls import reverse
@only_authenticated_user
def home_view(request):
    user=CustomUser.objects.filter(username=request.user.username)
    user_id = request.user.id
    user = get_object_or_404(CustomUser, id=user_id)
    if user.is_worker:
        try:
            worker=Worker.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            return render(request, 'attendance/home.html',{'users':user, 'user_id':user_id})
        
        worktime_entries = Worktime.objects.filter(worker=worker)
        return render(request, 'attendance/home.html',{'users':user, 'user_id': user_id,'worker': worker,'worktime_entries':worktime_entries})

    if user.is_company:
        company = Company.objects.get(user_id=user_id)
        form = KioskCodeForm()
        return render(request, 'attendance/home.html',{'users':user, 'company':company,'user_id': user_id,'form':form})
    #company = Company.objects.all() 
    #print("Company",company)
    
    
    #form = KioskCodeForm()
    #print("home view",user,worktime_entries)
    #return render(request, 'attendance/home.html',{'users':user,'company':company,'worktime_entries':worktime_entries, 'user_id': user_id})
    #return render(request, 'attendance/home.html')
    
@login_required
#@csrf_exempt
def add_worktime(request,worker = None):
    print("in add_worktime")
    if request.method == 'POST':
        user_id = request.POST.get('user_id')  # Assuming you pass the user_id in the request
        if worker is None:
            worker=Worker.objects.get(user_id=user_id)
        
        # Check if there is an existing entry for the user and current date
        existing_entry = Worktime.objects.filter(worker=worker, punch_out__isnull=True).first()
        
        if existing_entry:
            # Update the existing entry with punch_out time
            print("existing entry",existing_entry)
            existing_entry.punch_out = timezone.now()
            existing_entry.total_time = existing_entry.punch_out - existing_entry.punch_in
            existing_entry.save()
        else:
            # Create a new entry with punch_in time
            new_entry = Worktime(worker=worker, punch_in=timezone.now(), date=timezone.now().date())
            print("new entry",new_entry)
            new_entry.save()
            return JsonResponse({'status': 'success', 'entry_id': new_entry.id})
        return JsonResponse({'status': 'success'})
        
def get_worktime_details(request, entry_id):
    worktime = get_object_or_404(Worktime, id=entry_id)
    # Assuming you have appropriate fields in your Worktime model
    data = {
        'date': worktime.date,
        'punch_in': worktime.punch_in,
        'punch_out': worktime.punch_out,
        'total_time': worktime.total_time,
    }
    return JsonResponse(data)

@login_required   
def update_worktime_by_kiosk_code(request):
    print("update_worktime_by_kiosk_code")
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        print(request.body)
        #print(user_id)
        form = KioskCodeForm(request.POST)
        
        if form.is_valid():
            print(user_id)
            company=Company.objects.get(user_id=user_id)
            kiosk_code = form.cleaned_data['kiosk_code']
            try:
                worker=Worker.objects.get(kiosk_code=kiosk_code)
            except ObjectDoesNotExist:
                return JsonResponse({'status': 'failure','message':"Worker with that Kiosk Code was not found."})
            add_worktime(request,worker)
            print(f"{worker.firstname} {worker.lastname}")
            worker_info = f"{worker.firstname} {worker.lastname}"
            return JsonResponse({'status': 'success','worker':worker_info,'message':"Successfully updated worktime for: "})
    else:
        form = KioskCodeForm()
    
    return render(request, 'attendance/home.html', {'form': form})


@redirect_authenticated_user
def login_view(request):
    error = None
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request, username=form.cleaned_data['username_or_email'], password=form.cleaned_data['password'])
            if user:
                    print(user)
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

#@login_required
#def create_company(request):
#    if request.method == 'POST':
#        form = CreateCompanyForm(request.POST)
#        if form.is_valid():
#            print(form.cleaned_data)
#            name = form.cleaned_data['name']
#            address = form.cleaned_data['address']
#            company = Company(user = request.user, name = name, address = address)
#            print(company)
#            company.save()
#            request.user.is_company = True
#            request.user.save()
#    #request.user.bio = "testing"
#    else:
#        form = CreateCompanyForm()
#    print(request.user)
#    return render(request, 'attendance/login.html', {'form': form})
STEP_ONE = u'0'
STEP_TWO = u'1'
STEP_THREE = u'2'
STEP_FOUR = u'3'

class MyWizard(SessionWizardView):
    # Your form wizard itself; will not be called directly by urls.py, but rather wrapped in a function that provides the condition_dictionary

    # Change 1: Functions need to be stated before the dictionary
    def return_true(wizard): 
        return True  # A condition that is always True, for when you always want the form seen

    # Change 2: Only proceed with the logic if the step is valid
    def check_step_two(wizard): 
        step_1_info = wizard.get_cleaned_data_for_step(STEP_ONE)
        # Do something with info; can retrieve for any prior steps
        if step_1_info :
            if step_1_info['registration_choice'] == 'company':
                print("step_1_info",step_1_info)
                return True  # Show step 2
            else:
                return False  # or don't show
    def check_step_three(wizard): 
        step_1_info = wizard.get_cleaned_data_for_step(STEP_ONE)
        # Do something with info; can retrieve for any prior steps
        if step_1_info :
            if step_1_info['registration_choice'] == 'worker':
                print("step_1_info",step_1_info)
                return True  # Show step 2
            else:
                return False  # or don't show
    # Change 3: A condition must be added to skip an additional form
    condition_dict = {  
        STEP_ONE: return_true,  # Callable function that says to always show this step
        STEP_TWO: return_true,  # Conditional callable for verifying whether to show step two
        STEP_THREE: check_step_two,  # Conditional callable for verifying whether to show step three
        STEP_FOUR: check_step_three,  # Callable function that says to always show this step
    }
    
    form_list = [  
        (STEP_ONE, RegistrationChoiceForm),
        (STEP_TWO, CustomUserCreationForm),
        (STEP_THREE, RegisterCompanyForm),
        (STEP_FOUR, RegisterWorkerForm),
    ]

    

# Your original code
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
            company = Company.objects.create(
                user=user,
                name=data['name'],
                address=data['address']
            )
            user.is_company = True
            user.save()
            return redirect('attendance:login')
        elif data['registration_choice'] == 'worker':
            
            worker = Worker.objects.create(
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
    print("workers",workers)
    codes = []
    i=0
    while i<20:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        for worker in workers:
            codes.append(worker.kiosk_code)
        print("codes",codes)
        if code in codes:
            i+=1
        else:
            return code

#@redirect_authenticated_user
#def registeration_view(request):
#    if request.method == 'POST':
#        form = RegisterForm(request.POST or None)
#        if form.is_valid():
#            user = form.save(commit=False)
#            user.is_active = False
#            user.source = 'Register'
#            user.save(True)
#            print("User saved",user)
#    else:
#        form = RegisterForm()
#    return render(request, 'attendance/register.html', {'form': form})







@redirect_authenticated_user
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
