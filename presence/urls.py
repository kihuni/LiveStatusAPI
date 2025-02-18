from django.urls import path
from views import PresenceViewSet


urlpatterns = [
    path('api/users/<int:user_id>/presence/', PresenceViewSet.as_view({'get': 'retrieve', 'put': 'update'})),
]