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
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.shortcuts import (
    redirect,
    render,
)
from django.contrib.auth.decorators import login_required

from .forms import (
    CustomLoginForm,
    RegisterForm,
    ForgetPasswordEmailCodeForm,
    ChangePasswordForm,
    AddDataForm,
    CreateCompanyForm
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
@only_authenticated_user
def home_view(request):
    user=CustomUser.objects.filter(username=request.user.username)
    user_id = request.user.id
    user = get_object_or_404(CustomUser, id=user_id)
    try:
        worker=Worker.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        return render(request, 'attendance/home.html',{'users':user, 'user_id':user_id})
    print("worker",worker.firstname)
    #company = Company.objects.all() 
    #print("Company",company)
    
    worktime_entries = Worktime.objects.filter(worker=worker)
    #print("home view",user,worktime_entries)
    #return render(request, 'attendance/home.html',{'users':user,'company':company,'worktime_entries':worktime_entries, 'user_id': user_id})
    #return render(request, 'attendance/home.html')
    return render(request, 'attendance/home.html',{'users':user, 'user_id': user_id,'worker': worker,'worktime_entries':worktime_entries})
@login_required
#@csrf_exempt
def add_worktime(request):
    print("in add_worktime")
    if request.method == 'POST':
        user_id = request.POST.get('user_id')  # Assuming you pass the user_id in the request
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

@login_required
def create_company(request):
    if request.method == 'POST':
        form = CreateCompanyForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            company = Company(user = request.user, name = name, address = address)
            print(company)
            company.save()
            request.user.is_company = True
            request.user.save()
    #request.user.bio = "testing"
    else:
        form = CreateCompanyForm()
    print(request.user)
    return render(request, 'attendance/login.html', {'form': form})

@login_required
def add_data(request):
    if request.method == 'POST':
        form = AddDataForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            company = Company.objects.get(pk=form.cleaned_data['company'])
            
            worker = Worker(user = request.user,company=company,firstname=firstname, lastname=lastname,kiosk_code = generate_kiosk_code())
            #request.user.firstname = form.cleaned_data['firstname']
            #request.user.lastname = form.cleaned_data['lastname']
            #request.user.kiosk_code = generate_kiosk_code()
            #request.user.save()
            worker.save()
            request.user.is_worker = True
            request.user.save()
    #request.user.bio = "testing"
    else:
        form = AddDataForm()
    print(request.user)
    return render(request, 'attendance/login.html', {'form': form})
def generate_kiosk_code():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)) # TODO needs to be made unique
    return code

#    users = User.objects.filter(employer=_employer)
#    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
#    codes = []
#    i=0
#    while i<20:
#        for user in users:
#            codes.append(user.kiosk_code)
#        
#        if code in codes:
#            i+=1
#        else:
#            return code

@redirect_authenticated_user
def registeration_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.source = 'Register'
            user.save(True)
            print("User saved",user)
    else:
        form = RegisterForm()
    return render(request, 'attendance/register.html', {'form': form})







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
