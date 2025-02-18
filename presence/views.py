from models import Presence
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from serializers import PresenceSerializer


# Presence ViewSet
class PresenceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # Requires JWT auth

    def retrieve(self, request, user_id=None):
        if request.user.id != user_id:
            return Response({'error': 'You can only view your own presence data'}, status=403)
        try:
            presence = Presence.objects.get(user_id=user_id)
            serializer = PresenceSerializer(presence)
            return Response(serializer.data)
        except Presence.DoesNotExist:
            return Response({'error': 'Presence data not found'}, status=404)

    def update(self, request, user_id=None):
        if request.user.id != user_id:
            return Response({'error': 'You can only update your own presence data'}, status=403)
        try:
            presence = Presence.objects.get(user_id=user_id)
            serializer = PresenceSerializer(presence, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Presence.DoesNotExist:
            return Response({'error': 'Presence data not found'}, status=404)
