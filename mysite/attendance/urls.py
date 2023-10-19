from django.urls import path

from . import views
app_name = "attendance"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("register_user", views.register_user, name="register_user"),
    
    path("registuser_creationer_user", views.user_creation, name="user_creation"),
    
    path("register_company", views.register_company, name="register_company"),
    path("<int:user_id>/user_main_page",views.user_main_page, name="user_main_page"),
    path("<int:company_id>/company_info",views.company_info, name="company_info")
]