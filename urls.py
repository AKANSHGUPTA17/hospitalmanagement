from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.authentication.urls', namespace='auth')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('patients/', include('apps.patients.urls', namespace='patients')),
    path('billing/', include('apps.billing.urls', namespace='billing')),
    path('doctors/', include('apps.doctors.urls', namespace='doctors')),
    path('appointments/', include('apps.appointments.urls', namespace='appointments')),
    # API endpoints
    path('api/v1/auth/', include('apps.authentication.api_urls')),
    path('api/v1/patients/', include('apps.patients.api_urls')),
    path('api/v1/billing/', include('apps.billing.api_urls')),
    path('api/v1/doctors/', include('apps.doctors.api_urls')),
    path('api/v1/appointments/', include('apps.appointments.api_urls')),
    # Root redirect
    path('', include('apps.dashboard.urls', namespace='dashboard_root')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
