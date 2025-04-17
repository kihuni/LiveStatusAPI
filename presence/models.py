# presence/models.py

from django.db import models
from users.models import CustomUser
from django.utils import timezone  # Ensure this import is present

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
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='presence_records'
    )
    status = models.CharField(
        max_length=10,
        choices=Presence.STATUS_CHOICES
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set changed_at manually if it's not already set
        if not self.changed_at:
            self.changed_at = timezone.now()  # Now this should work

        # Calculate duration of the previous status if this isn't the first record
        previous_record = PresenceRecord.objects.filter(
            user=self.user,
            changed_at__lt=self.changed_at
        ).order_by('-changed_at').first()

        if previous_record:
            delta = self.changed_at - previous_record.changed_at
            self.duration = int(delta.total_seconds())
        else:
            self.duration = 0  # First record, no previous duration

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.status} at {self.changed_at} (Duration: {self.duration}s)"