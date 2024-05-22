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
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .views import activateEmail, get_company_from_user, generate_kiosk_codes

def validate_user_data(user_data):
    required_fields = {'username', 'email', 'firstname', 'lastname', 'role'}
    errors = []
    for i, user in enumerate(user_data):
        missing_fields = [field for field in required_fields if not user.get(field)]
        if missing_fields:
            errors.append(f"Row {i+1}: Missing fields - {', '.join(missing_fields)}")
        if 'role' in user and user['role'] not in ['manager', 'worker']:
            errors.append(f"Row {i+1}: Invalid role - {user['role']}. Must be 'manager' or 'worker'.")
        if 'email' in user and user.get('email'):
            try:
                validate_email(user['email'])
            except ValidationError:
                errors.append(f"Row {i+1}: Invalid email format - {user['email']}")

    return errors

def parse_csv(uploaded_file):
    with io.TextIOWrapper(uploaded_file.file, encoding="utf-8-sig", errors='replace',newline='\n') as text_file:
        reader = csv.DictReader(text_file)
        user_data = [row for row in reader]
        return user_data

def parse_json(uploaded_file):
    f = TextIOWrapper(uploaded_file.file, encoding='utf-8', errors='replace')
    user_data = json.load(f)
    return user_data

def parse_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)
    user_data = [row.to_dict() for index, row in df.iterrows()]
    return user_data

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            file_extension = uploaded_file.name.split('.')[-1].lower()
            print(file_extension)
            try:
                if file_extension == 'csv':
                    user_data = parse_csv(uploaded_file)
                elif file_extension == 'json':
                    user_data = parse_json(uploaded_file)
                elif file_extension == 'xlsx':
                    user_data = parse_excel(uploaded_file)
                else:
                    raise ValueError("Unsupported file format")
                
                errors = validate_user_data(user_data)
                if errors:
                        raise ValueError(errors)
                create_users(request, user_data)
                data = {'form': form, 'message': "File uploaded successfully"}
                return render(request, 'attendance/file_upload.html', data)

            except ValueError as e:
                data = {'form': form, 'message': f"Error in uploaded file: {e}"}
                return render(request, 'attendance/file_upload.html', data)
        else:
            return render(request, 'attendance/file_upload.html', {'form': form,'message':"Invalid file upload form"})
    
    else:
        form = FileUploadForm()
        return render(request, 'attendance/file_upload.html', {'form': form,})

def create_users(request, users_data):
    errors = []
    for i, user_data in enumerate(users_data):
        if CustomUser.objects.filter(username=user_data['username']).exists():
            errors.append(f"Row {i+1}: Username '{user_data['username']}' already exists.")
        if CustomUser.objects.filter(email=user_data['email']).exists():
            errors.append(f"Row {i+1}: Email '{user_data['email']}' already exists.")
    if errors:
        raise ValueError(errors)
    
    passwords = generate_random_passwords(len(users_data))
    company = get_company_from_user(request.user.id)
    kiosk_codes = generate_kiosk_codes(company, len(users_data))
    for i, user_data in enumerate(users_data):
        user = CustomUser.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=passwords[i],
            password_change_required=True,
            is_active=False,
            is_worker=True
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

def generate_random_passwords(amount=1):
    pwo = PasswordGenerator()
    pwo.minlen = 30
    pwo.maxlen = 30
    passwords = [pwo.generate() for i in range(amount)]
    print(passwords)
    return passwords