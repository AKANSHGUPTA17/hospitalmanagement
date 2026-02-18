from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.AppointmentListCreateView.as_view()),
    path('<int:pk>/', api_views.AppointmentDetailView.as_view()),
]
