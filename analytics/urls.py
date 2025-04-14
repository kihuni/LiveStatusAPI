# analytics/urls.py

from django.urls import path
from .views import ResponseTimePredictionView

urlpatterns = [
    path('users/<uuid:userId>/response-time-prediction/', ResponseTimePredictionView.as_view(), name='response-time-prediction'),
]