from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.PatientListCreateView.as_view()),
    path('<int:pk>/', api_views.PatientDetailView.as_view()),
    path('search/', api_views.patient_search),
    path('<int:pk>/vitals/', api_views.PatientVitalsView.as_view()),
]
