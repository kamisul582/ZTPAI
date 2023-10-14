from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:user_id>/user_info",views.user_info, name="user_info"),
    path("<int:company_id>/company_info",views.company_info, name="company_info")
]