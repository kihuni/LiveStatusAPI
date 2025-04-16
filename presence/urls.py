# presence/urls.py

from django.urls import path
from .views import PresenceView,PresenceUpdateView

urlpatterns = [
    path('users/<uuid:userId>/presence/', PresenceView.as_view(), name='user-presence'),
    path("presence/", PresenceUpdateView.as_view(), name="presence-update"),
]