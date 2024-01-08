from django.urls import path
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf.urls.static import static
from .views import (
    home_view,
    login_view,
    logout_view,
    RegistrationWizardView,
    reset_new_password_view,
    add_worktime,
    get_worktime_details,
    update_worktime_by_kiosk_code,
)
# router = DefaultRouter()
# router.register('data', RegistrationWizardView, basename='data')
# urlpatterns = router.urls
app_name = 'attendance'
schema_view = get_schema_view(
    openapi.Info(
        title="Attendance API",
        default_version='v1',),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('change-password/', reset_new_password_view, name='reset_new_password_view'),
    path('worktime-by-kiosk-code/', update_worktime_by_kiosk_code, name='update_worktime_by_kiosk_code'),
    path('logout/', logout_view, name='logout'),
    path('register/', RegistrationWizardView.as_view(), name='register'),
    path('new-password/', reset_new_password_view, name='reset_new_password'),
    path('add-worktime/', add_worktime, name='add_worktime'),
    path('get-worktime-details/<int:entry_id>/', get_worktime_details, name='get_worktime_details'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
