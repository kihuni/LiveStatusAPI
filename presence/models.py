from django.db import models
from users.models import CustomUser

class Presence(models.Model):
    STATUS_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('away', 'Away'),
        ('busy', 'Busy'),
    )

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='presence',
        primary_key=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='offline'
    )
    last_seen = models.DateTimeField(auto_now=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.status}"
    
    

class PresenceRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='presence_records')
    status = models.CharField(max_length=10, choices=Presence.STATUS_CHOICES)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.status} @ {self.recorded_at}"