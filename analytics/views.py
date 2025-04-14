# analytics/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.db.models import Avg  # Correct import for Avg
from users.models import CustomUser
from presence.models import Presence
from analytics.models import ResponseHistory
from analytics.serializers import ResponseTimePredictionSerializer

class ResponseTimePredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, userId, *args, **kwargs):
        # Retrieve the user and their current presence status
        try:
            user = CustomUser.objects.get(id=userId)
            presence = Presence.objects.get(user=user)
        except (CustomUser.DoesNotExist, Presence.DoesNotExist):
            raise serializers.ValidationError("User or presence data not found.")

        # Get the user's current presence status
        current_status = presence.status

        # Query response history for this user
        response_history = ResponseHistory.objects.filter(user=user)

        if not response_history.exists():
            # No historical data; return a default prediction
            predicted_time = 600  # 10 minutes
        else:
            # Try to predict based on the current presence status
            status_specific_history = response_history.filter(presence_status=current_status)
            if status_specific_history.count() >= 5:
                # Enough data for a status-specific prediction
                avg_response_time = status_specific_history.aggregate(
                    avg_time=Avg('response_time')  # Use Avg directly
                )['avg_time']
                predicted_time = int(avg_response_time)
            else:
                # Fall back to overall average
                avg_response_time = response_history.aggregate(
                    avg_time=Avg('response_time')  # Use Avg directly
                )['avg_time']
                predicted_time = int(avg_response_time)

        # Serialize the prediction
        serializer = ResponseTimePredictionSerializer({
            'predicted_response_time': predicted_time
        })
        return Response(serializer.data)