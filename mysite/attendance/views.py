from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from .models import User, Company
import random, string
import json
# Create your views here.
def index(request):
    #return HttpResponse("Hello, world. You're at the attendance index.")
    return render(request, "attendance/login.html")

def login(request):
    print(request)
    print("test login")
    if request.method == "GET":
        return render(request, "attendance/login.html")
    elif request.method == "POST":
        dictionary = request.POST
        print(dictionary)
        if 'login_as_company' in dictionary.keys():
            print('company login')
    user = authenticate(username = dictionary['email'], password = dictionary['password'])
    print(user)
    if user is not None:
        print("logged in")
    else:
        print("user not found")
    return render(request, "attendance/user_main_page.html")
def register_user(request):
    if request.method == "GET":
        return render(request, "attendance/register_user.html")
    elif request.method == "POST":
        
        dictionary = request.POST
        print(dictionary)
        if dictionary['password'] != dictionary['confirmed_password']:
            print(dictionary['password'], dictionary['confirmed_password'])
            context = {"message": "passwords do not match"}
            return render(request, "attendance/register_user.html",context)
        user_creation(request,dictionary['email'],dictionary['password'],dictionary['name'],dictionary['surname'],dictionary['employer_id'])
    context = {"message": "User registered"}
    #return render(request, "attendance/register_user.html",context)
    return JsonResponse(context, safe=False)
    

def register_company(request):
    if request.method == "GET":
        return render(request, "attendance/register_company.html")
    elif request.method == "POST":
        dictionary = request.POST
        if dictionary['password'] != dictionary['confirmed_password']:
            print(dictionary['password'], dictionary['confirmed_password'])
            context = {"message": "passwords do not match"}
            return render(request, "attendance/register_company.html",context)
        company = Company.objects.create(email = dictionary['email'],
                               password =dictionary['password'],
                               company_name = dictionary['company_name'],
                               company_address = dictionary['company_address'])
        print(company)
    context = {"message": "Company registered"}
    return render(request, "attendance/register_company.html",context)

def user_creation(request, _email, _password, _name, _surname, _employer):
    #user = User(email = email, password = password, name = name, surname = surname, employer = employer)
    #context = {"email": email,"password": password,"name": name,"surname": surname,"employer": employer,}
    print(request, _email, _password, _name, _surname, _employer)
    code = generate_kiosk_code(_employer)
    user = User.objects.create(email = _email,
                               password = _password,
                               name = _name,
                               surname = _surname,
                               employer = Company.objects.get(pk = _employer),
                               kiosk_code = code)
    print(user)
    

def generate_kiosk_code(_employer):
    users = User.objects.filter(employer=_employer)
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    codes = []
    i=0
    while i<20:
        for user in users:
            codes.append(user.kiosk_code)
        
        if code in codes:
            i+=1
        else:
            return code
    
@login_required(login_url="/attendance/login")
def user_main_page(request,user_id):
    user = User.objects.get(pk=user_id)
    context = {"user": user}
    return render(request, f"attendance/{user_id}/user_main_page.html", context)

def user_info(request, user_id):
    user = User.objects.get(pk=user_id)
    return HttpResponse(user)



def company_info(request, company_id):
    company = Company.objects.get(pk=company_id)
    return HttpResponse(company)
