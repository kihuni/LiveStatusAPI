# presence/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser
from .models import Presence

@receiver(post_save, sender=CustomUser)
def create_initial_presence(sender, instance, created, **kwargs):
    if created:
        Presence.objects.create(user=instance, status="offline", device_type="unknown")