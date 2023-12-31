from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    home_view,
    login_view,
    logout_view,
    RegistrationWizardView,
    reset_new_password_view,
    add_data,
    add_worktime,
    get_worktime_details,
)

app_name = 'attendance'

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    #path('register/', registeration_view, name='register'),
    path('register/', RegistrationWizardView.as_view(), name='register'),
    path('new-password/', reset_new_password_view, name='reset_new_password'),
    path('add-data/', add_data, name='add_data'),
    #path('create-company/', create_company, name='create_company'),
    path('add-worktime/', add_worktime, name='add_worktime'),
    path('get_worktime_details/<int:entry_id>/', get_worktime_details, name='get_worktime_details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
