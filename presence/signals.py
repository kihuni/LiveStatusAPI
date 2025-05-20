# presence/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Presence

@receiver(post_save, sender=Presence)
def broadcast_presence_update(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"presence_{instance.user_id}",
            {
                "type": "presence_update",
                "data": {
                    "user_id": str(instance.user_id),
                    "status": instance.status,
                    "device_type": instance.device_type,
                    "last_seen": instance.last_seen.isoformat(),
                    "predicted_response_time": instance.predicted_response_time,
                    "engagement_score": instance.user.engagement_score,
                },
            },
        )
        
@receiver(post_save, sender=Presence)
def update_engagement_score(sender, instance, created, **kwargs):
    if created and instance.status == "online":
        instance.user.engagement_score += 0.1
        instance.user.save(update_fields=["engagement_score"])
        # Include in WebSocket broadcast
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"presence_{instance.user_id}",
            {
                "type": "presence_update",
                "data": {
                    "user_id": str(instance.user_id),
                    "status": instance.status,
                    "device_type": instance.device_type,
                    "last_seen": instance.last_seen.isoformat(),
                    "predicted_response_time": instance.predicted_response_time,
                    "engagement_score": instance.user.engagement_score,
                },
            },
        )