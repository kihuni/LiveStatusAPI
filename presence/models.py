# presence/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Presence(models.Model):
    STATUS_CHOICES = (
        ("online", "Online"),
        ("away", "Away"),
        ("offline", "Offline"),
        ("busy", "Busy"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="presence_records")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    device_type = models.CharField(max_length=50, blank=True)
    last_seen = models.DateTimeField(auto_now_add=True)
    predicted_response_time = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "presence_record"
        indexes = [
            models.Index(fields=["user", "last_seen"]),
        ]