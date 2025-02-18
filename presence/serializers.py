from rest_framework import serializers, viewsets, routers
from models import Presence


# Serializer for Presence Data
class PresenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presence
        fields = ['user', 'status', 'last_seen', 'device_type']
        read_only_fields = ['last_seen']
