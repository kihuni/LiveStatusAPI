# presence/tests.py
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken
from users.models import CustomUser
from .models import Presence
from .consumers import PresenceConsumer

class PresenceConsumerTests(TestCase):
    async def setUp(self):
        self.user = await database_sync_to_async(CustomUser.objects.create_user)(
            email="test@example.com",
            username="testuser",
            password="Test123!@#",
            is_verified=True,
            is_active=True,
        )
        self.token = str(AccessToken.for_user(self.user))
        await database_sync_to_async(Presence.objects.create)(
            user=self.user, status="online", device_type="desktop"
        )

    async def test_presence_consumer(self):
        communicator = WebsocketCommunicator(
            PresenceConsumer.as_asgi(), f"/ws/presence/{self.user.id}/?token={self.token}"
        )
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        response = await communicator.receive_json_from()
        self.assertEqual(response["data"]["status"], "online")
        self.assertEqual(response["data"]["user_id"], str(self.user.id))
        await communicator.disconnect()

    async def test_unauthorized_access(self):
        communicator = WebsocketCommunicator(
            PresenceConsumer.as_asgi(), f"/ws/presence/{self.user.id}/?token=invalid"
        )
        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)