# analytics/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.db.models import Avg
from django.utils import timezone
from users.models import CustomUser
from presence.models import Presence, PresenceRecord  # Import PresenceRecord
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

        # Calculate session duration (time since last status change)
        latest_presence_record = PresenceRecord.objects.filter(
            user=user,
            status=current_status
        ).order_by('-changed_at').first()

        session_duration = 0  # Default to 0 if no record exists
        if latest_presence_record:
            delta = timezone.now() - latest_presence_record.changed_at
            session_duration = int(delta.total_seconds())  # Duration in seconds

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
                    avg_time=Avg('response_time')
                )['avg_time']
                predicted_time = avg_response_time if avg_response_time is not None else 600
            else:
                # Fall back to overall average
                avg_response_time = response_history.aggregate(
                    avg_time=Avg('response_time')
                )['avg_time']
                predicted_time = avg_response_time if avg_response_time is not None else 600

            # Adjust prediction based on session duration
            # If the user has been in the current status for a long time (> 1 hour),
            # they might be idle, so increase the predicted time by 20%
            if session_duration > 3600:  # 1 hour
                predicted_time *= 1.2

            predicted_time = int(predicted_time)

        # Serialize the prediction
        serializer = ResponseTimePredictionSerializer({
            'predicted_response_time': predicted_time
        })
        return Response(serializer.data)