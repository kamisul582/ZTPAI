from django.shortcuts import render
from django.http import HttpResponse
from .models import User, Company

# Create your views here.
def index(request):
    #return HttpResponse("Hello, world. You're at the attendance index.")
    return render(request, "attendance/login.html")

def login(request):
    print(request)
    print("test login")
    return render(request, "attendance/login.html")

def register_user(request):
    if request.method == "GET":
        return render(request, "attendance/register_user.html")
    elif request.method == "POST":
        dictionary = request.POST
        user_creation(request,dictionary['email'],dictionary['password'],dictionary['name'],dictionary['surname'],dictionary['employer_id'])
    return render(request, "attendance/register_user.html")
    

def register_company(request):
    return render(request, "attendance/register_company.html")

def user_creation(request, _email, _password, _name, _surname, _employer):
    #user = User(email = email, password = password, name = name, surname = surname, employer = employer)
    #context = {"email": email,"password": password,"name": name,"surname": surname,"employer": employer,}
    print(request, _email, _password, _name, _surname, _employer)
    user = User.objects.create(email = _email,
                               password = _password,
                               name = _name,
                               surname = _surname,
                               employer = Company.objects.get(pk = _employer))
    print(user)
    #return render(request, "attendance/user_main_page.html", context)
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
