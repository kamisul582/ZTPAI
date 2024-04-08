import csv
import json
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from .forms import FileUploadForm
from io import TextIOWrapper

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        file_extension = uploaded_file.name.split('.')[-1].lower()
        form = FileUploadForm(request.POST, request.FILES)
        print(file_extension)
        if form.is_valid():
            if file_extension == 'csv':
                user_data = parse_csv(uploaded_file)
            elif file_extension == 'json':
                user_data = parse_json(uploaded_file)
            elif file_extension == 'xlsx':
                user_data = parse_excel(uploaded_file)
            else:
                data = {'form': form, 'message': "Unsupported file format"}
                return render(request, 'attendance/file_upload.html', data)
        else:
            return render(request, 'attendance/file_upload.html', {'form': form})
        data = {'form': form, 'message': "File uploaded successfully"}
        return render(request, 'attendance/file_upload.html', data)
    else:
        form = FileUploadForm()
        return render(request, 'attendance/file_upload.html', {'form': form})

def parse_csv(uploaded_file):
    user_data = []
    
    reader = csv.DictReader(uploaded_file)
    for row in reader:
        user_data.append(row)
    print(user_data)
    return user_data

def parse_json(uploaded_file):
    f = TextIOWrapper(uploaded_file.file, encoding='ascii', errors='replace')
    user_data = json.load(f)
    print(user_data)
    return user_data

def parse_excel(uploaded_file):
    user_data = []
    df = pd.read_excel(uploaded_file)
    for index, row in df.iterrows():
        user_data.append(row.to_dict())
    print(user_data)
    return user_data
