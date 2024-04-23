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
    get_employees,
    get_worker_worktime,
    get_user_ids,
    add_subordinates,
    activate,
    get_employed_user_ids_json,
)
from .charts import template, line_chart_json
from .file_handlers import upload_file
from .worktime_report import WorktimeExportView,worktime_export
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
    path('get-worker-worktime/<int:user_id>/', get_worker_worktime, name='get_worker_worktime'),
    path('get-employees/', get_employees, name='get_employees'),
    path('add-subordinates/', add_subordinates, name='add_subordinates'),
    path('get-employees/<str:sort>/<str:filter>/', get_employees, name='get_employees'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('charts', template, name='charts'),
    path('chartJSON', line_chart_json, name='line_chart_json'),
    path('get-user-ids/', get_user_ids, name='get_user_ids'),
    path('get-employed-user-ids/', get_employed_user_ids_json, name='get_employed_user_ids_json'),
    path('upload/', upload_file, name='upload_file'),
    path('report', WorktimeExportView.as_view(),name='report'),
    path('worktime-export/', worktime_export, name='worktime_export'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
