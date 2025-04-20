# presence/views.py

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from .models import Presence
from .serializers import PresenceSerializer, PresenceUpdateSerializer
from .permissions import IsOwnerOrAdmin

class PresenceUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Presence.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return PresenceUpdateSerializer
        return PresenceSerializer

    def get_object(self):
        user_id = self.kwargs["userId"] 
        try:
            presence = Presence.objects.get(user__id=user_id)
        except Presence.DoesNotExist:
            raise NotFound("Presence not found for the user.")

        self.check_object_permissions(self.request, presence)
        return presence