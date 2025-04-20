# presence/urls.py

from django.urls import path
from .views import PresenceUpdateView

urlpatterns = [
    path('users/<uuid:userId>/presence/', PresenceUpdateView.as_view(), name='user-presence'),
]
