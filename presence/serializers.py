# presence/serializers.py
from rest_framework import serializers
from .models import Presence
from django.contrib.auth import get_user_model

User = get_user_model()

class PresenceDataSerializer(serializers.ModelSerializer):
    engagement_score = serializers.FloatField(source="user.engagement_score")
    user_id = serializers.CharField(source="user.id")

    class Meta:
        model = Presence
        fields = ["user_id", "status", "device_type", "last_seen", "predicted_response_time", "engagement_score"]