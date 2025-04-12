from django.urls import path
from .views import RegisterView, VerifyEmailView, CustomTokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
]
