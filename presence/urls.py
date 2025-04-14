# presence/urls.py

from django.urls import path
from .views import PresenceView

urlpatterns = [
    path('users/<uuid:userId>/presence/', PresenceView.as_view(), name='user-presence'),
]