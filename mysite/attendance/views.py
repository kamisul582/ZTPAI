from django.shortcuts import render
from django.http import HttpResponse
from .models import User

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the attendance index.")

def user_info(request, user_id):
    user = User.objects.get(pk=id)
    return HttpResponse(f"The User info is:{User}")# {temp_user.email}, {temp_user.name}, {temp_user.surname}")
             
#def user_info(request, user_id):
 #   User
 #   return HttpResponse(f"The User info is:{user_id}")
