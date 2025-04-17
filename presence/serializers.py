# presence/serializers.py

from rest_framework import serializers
from .models import Presence
from analytics.views import ResponseTimePredictionView  # Import to reuse prediction logic
from rest_framework.request import Request
from django.http import HttpRequest

class PresenceSerializer(serializers.ModelSerializer):
    predicted_response_time = serializers.IntegerField(read_only=True)  # In seconds
    predicted_response_time_display = serializers.CharField(read_only=True)  # Human-readable format

    class Meta:
        model = Presence
        fields = ['status', 'last_seen', 'device_type', 'predicted_response_time', 'predicted_response_time_display']
        read_only_fields = ['last_seen']
        
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Reuse the ResponseTimePredictionView logic to get the prediction
        request = self.context.get('request')
        if not request:
            # Create a dummy request if none is provided (e.g., for testing)
            request = Request(HttpRequest())
            request.user = instance.user  # Set the user for permission checks

        prediction_view = ResponseTimePredictionView()
        prediction_response = prediction_view.get(request, userId=str(instance.user.id))

        # Add prediction data to the representation
        prediction_data = prediction_response.data
        representation['predicted_response_time'] = prediction_data['predicted_response_time']
        representation['predicted_response_time_display'] = prediction_data['predicted_response_time_display']

        return representation
        
        
        
        
        
        
        
        
  