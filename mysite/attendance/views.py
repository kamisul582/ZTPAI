from django.shortcuts import render
from django.http import HttpResponse
from .models import User, Company

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the attendance index.")

def user_info(request, user_id):
    user = User.objects.get(pk=user_id)
    return HttpResponse(user)



def company_info(request, company_id):
    company = Company.objects.get(pk=company_id)
    return HttpResponse(company)
#def user_info(request, user_id):
 #   User
 #   return HttpResponse(f"The User info is:{user_id}")
