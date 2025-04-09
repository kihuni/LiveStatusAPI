from django.urls import path
from .views import UserView, RegisterView, VerifyEmailView, CustomTokenObtainPairView

urlpatterns = [
    path('users/', UserView.as_view(), name='user-list'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
]
