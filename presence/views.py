from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from .models import Presence
from .serializers import PresenceSerializer
from presence.models import PresenceRecord
from .permissions import IsOwnerOrAdmin


class PresenceView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PresenceSerializer

    def get_object(self):
        user_id = self.kwargs.get('userId')
        try:
            presence = Presence.objects.get(user__id=user_id)
            return presence
        except (Presence.DoesNotExist):
            raise serializers.ValidationError("User or presence data not found.")
        
class PresenceUpdateView(generics.UpdateAPIView):
    queryset = Presence.objects.all()
    serializer_class = PresenceSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        # Only admins can update any presence, others must match the user ID
        user_id = self.kwargs["user_id"]
        try:
            presence = Presence.objects.get(user__id=user_id)
        except Presence.DoesNotExist:
            raise NotFound("Presence not found for the user.")

        self.check_object_permissions(self.request, presence)
        return presence
