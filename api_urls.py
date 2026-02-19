from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.BillListCreateView.as_view()),
    path('<int:pk>/', api_views.BillDetailView.as_view()),
    path('<int:pk>/payments/', api_views.PaymentListCreateView.as_view()),
    path('reports/daily/', api_views.daily_revenue_report),
    path('reports/monthly/', api_views.monthly_revenue_report),
]
