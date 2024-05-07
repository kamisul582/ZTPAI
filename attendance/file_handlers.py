import csv
import io
import json
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from .forms import FileUploadForm
from io import TextIOWrapper
from .models import CustomUser, Worker
from password_generator import PasswordGenerator
from .views import activateEmail, get_company_from_user, generate_kiosk_codes
def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        file_extension = uploaded_file.name.split('.')[-1].lower()
        form = FileUploadForm(request.POST, request.FILES)
        print(file_extension)
        if not form.is_valid():
            return render(request, 'attendance/file_upload.html', {'form': form})
        if file_extension == 'csv':
            user_data = parse_csv(uploaded_file)
        elif file_extension == 'json':
            user_data = parse_json(uploaded_file)
        elif file_extension == 'xlsx':
            user_data = parse_excel(uploaded_file)
        else:
            data = {'form': form, 'message': "Unsupported file format"}
            return render(request, 'attendance/file_upload.html', data)
            
        create_users(request,user_data)
        data = {'form': form, 'message': "File uploaded successfully"}
        return render(request, 'attendance/file_upload.html', data)
    
    else:
        form = FileUploadForm()
        return render(request, 'attendance/file_upload.html', {'form': form})

def create_users(request,users_data):
    passwords = generate_random_passwords(len(users_data))
    company = get_company_from_user(request.user.id)
    kiosk_codes = generate_kiosk_codes(company,len(users_data))
    i = 0
    for user_data in users_data:
        user = CustomUser.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=passwords[i],
                password_change_required = True,
                is_active = False,
                is_worker = True
            )
        if user_data['role'] == 'manager':
            user.is_manager = True
        user.save()
        activateEmail(request, user, user_data['email'])
        Worker.objects.create(
                user=user,
                company=company,
                firstname=user_data['firstname'],
                lastname=user_data['lastname'],
                kiosk_code=kiosk_codes[i]
            )
        i+=1
def parse_csv(uploaded_file):
    with io.TextIOWrapper(uploaded_file, encoding="utf-8", newline='\n') as text_file:
        reader = csv.DictReader(text_file)                
        user_data = [ row for row in reader]
        print(user_data)
        return user_data

def parse_json(uploaded_file):
    f = TextIOWrapper(uploaded_file.file, encoding='ascii', errors='replace')
    user_data = json.load(f)
    print(user_data)
    return user_data

def parse_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)
    user_data = [row.to_dict() for index, row in df.iterrows()]
    print(user_data)
    return user_data

def generate_random_passwords(amount = 1):
    pwo = PasswordGenerator()
    pwo.minlen = 30
    pwo.maxlen = 30
    passwords = [pwo.generate() for i in range(amount)]
    return passwords
    
