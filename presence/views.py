from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import Presence
from .serializers import PresenceSerializer

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