from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('create/', views.bill_create, name='bill_create'),
    path('<int:pk>/', views.bill_detail, name='bill_detail'),
    path('<int:pk>/edit/', views.bill_edit, name='bill_edit'),
    path('<int:pk>/payment/', views.add_payment, name='add_payment'),
    path('<int:pk>/pdf/', views.bill_pdf, name='bill_pdf'),
    path('reports/revenue/', views.revenue_report, name='revenue_report'),
]
