from django.shortcuts import render
from django.http import HttpResponse
from .models import User, Company

# Create your views here.
def index(request):
    #return HttpResponse("Hello, world. You're at the attendance index.")
    return render(request, "attendance/login.html")

def login(request):
    return render(request, "attendance/login.html")

def register_user(request):
    return render(request, "attendance/register_user.html")

def register_company(request):
    return render(request, "attendance/register_company.html")

def user_creation(request, email, password, name, surname, employer):
    #user = User(email = email, password = password, name = name, surname = surname, employer = employer)
    context = {"email": email,"password": password,"name": name,"surname": surname,"employer": employer,}
    return render(request, "attendance/user_main_page.html", context)
def user_main_page(request,user_id):
    user = User.objects.get(pk=user_id)
    context = {"user": user}
    return render(request, "attendance/user_main_page.html", context)

def user_info(request, user_id):
    user = User.objects.get(pk=user_id)
    return HttpResponse(user)



def company_info(request, company_id):
    company = Company.objects.get(pk=company_id)
    return HttpResponse(company)
