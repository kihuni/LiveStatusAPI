# presence/consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.throttling import AnonRateThrottle

from .models import Presence
import logging
import json

logger = logging.getLogger(__name__)
User = get_user_model()

class PresenceConsumer(AsyncJsonWebsocketConsumer):
    
    throttle_class = AnonRateThrottle
    throttle_rate = "100/hour"

    """
    WebSocket consumer for real-time presence updates for a specific user.
    """
    async def connect(self):
         
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group_name = f"presence_{self.user_id}"

        # Authenticate using JWT from query string
        token = self.scope["query_string"].decode().split("token=")[-1] if "token=" in self.scope["query_string"].decode() else None
        user = await self.authenticate_user(token)
        if not user or (str(user.id) != self.user_id and not user.is_staff):
            await self.close(code=4001)  # Unauthorized
            return

        # Join the presence group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"WebSocket connected for user: {self.user_id}")

        # Send current presence
        presence = await self.get_latest_presence()
        if presence:
            await self.send_json({
                "type": "presence_update",
                "data": {
                    "user_id": self.user_id,
                    "status": presence.status,
                    "device_type": presence.device_type,
                    "last_seen": presence.last_seen.isoformat(),
                    "predicted_response_time": presence.predicted_response_time,
                    "engagement_score": user.engagement_score,
                },
            })

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"WebSocket disconnected for user: {self.user_id}")

    async def receive_json(self, content):
        # Optionally handle client-initiated presence updates
        if content.get("type") == "presence_update":
            await self.update_presence(content.get("data", {}))

    async def presence_update(self, event):
        # Broadcast presence updates to the group
        await self.send_json(event["data"])

    @database_sync_to_async
    def authenticate_user(self, token):
        try:
            validated_token = JWTAuthentication().get_validated_token(token)
            user = JWTAuthentication().get_user(validated_token)
            return user
        except AuthenticationFailed:
            return None

    @database_sync_to_async
    def get_latest_presence(self):
        try:
            return Presence.objects.filter(user_id=self.user_id).order_by("-last_seen").first()
        except Presence.DoesNotExist:
            return None

    @database_sync_to_async
    def update_presence(self, data):
        status = data.get("status")
        device_type = data.get("device_type")
        if status in ["online", "away", "offline", "busy"]:
            Presence.objects.create(
                user_id=self.user_id,
                status=status,
                device_type=device_type or "unknown",
                predicted_response_time=data.get("predicted_response_time"),
            )