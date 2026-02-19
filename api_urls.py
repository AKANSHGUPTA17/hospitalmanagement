from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views

urlpatterns = [
    path('token/', obtain_auth_token, name='api_token'),
    path('users/', api_views.UserListCreateAPIView.as_view(), name='api_users'),
    path('users/<int:pk>/', api_views.UserDetailAPIView.as_view(), name='api_user_detail'),
    path('me/', api_views.CurrentUserAPIView.as_view(), name='api_me'),
]
