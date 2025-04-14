from rest_framework import serializers
from .models import Presence

class PresenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presence
        fields = ['status', 'last_seen', 'device_type']