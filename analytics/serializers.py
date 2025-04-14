from rest_framework import serializers

class ResponseTimePredictionSerializer(serializers.Serializer):
    predicted_response_time = serializers.IntegerField()  # In seconds
    predicted_response_time_display = serializers.CharField(read_only=True)  # Human-readable format, read-only

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        seconds = representation['predicted_response_time']
        # Convert seconds to a human-readable format
        if seconds < 60:
            representation['predicted_response_time_display'] = f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            representation['predicted_response_time_display'] = f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            hours = seconds // 3600
            representation['predicted_response_time_display'] = f"{hours} hour{'s' if hours != 1 else ''}"
        return representation