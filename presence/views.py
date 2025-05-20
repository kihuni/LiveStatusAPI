# presence/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Presence
from .serializers import PresenceDataSerializer
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema

class UserPresenceView(generics.RetrieveAPIView):
    queryset = Presence.objects.select_related("user")
    serializer_class = PresenceDataSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "user_id"

    @extend_schema(
        summary="Get user presence",
        description="Retrieve the latest presence data for a user. WebSocket endpoint: ws://your-domain.com/ws/presence/{user_id}/?token=<JWT_TOKEN>",
    )
    def get(self, request, *args, **kwargs):
        presence = self.get_object()
        serializer = self.get_serializer(presence)
        data = serializer.data
        data["websocket_url"] = f"ws://your-domain.com/ws/presence/{self.kwargs['user_id']}/?token=<JWT_TOKEN>"
        return Response(data)