from django.db import models
from users.models import CustomUser

class ResponseHistory(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='response_history'
    )
    message_id = models.CharField(max_length=36)  # Unique identifier for the message
    received_at = models.DateTimeField()  # When the message was received
    responded_at = models.DateTimeField()  # When the user responded
    presence_status = models.CharField(max_length=10)  # User's presence status at the time of response
    response_time = models.IntegerField()  # Response time in seconds (computed)

    def save(self, *args, **kwargs):
        # Compute response_time in seconds
        if self.received_at and self.responded_at:
            delta = self.responded_at - self.received_at
            self.response_time = int(delta.total_seconds())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - Message {self.message_id} - {self.response_time}s"