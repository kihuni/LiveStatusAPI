from channels.generic.websocket import AsyncWebsocketConsumer
import json

class PresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'presence_updates'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Handle incoming messages from the client (if needed)
        pass

    async def presence_update(self, event):
        # Send presence updates to the client
        await self.send(text_data=json.dumps({
            'event_type': 'presence_status_changed',
            'user_id': event['user_id'],
            'status': event['status'],
            'device_type': event['device_type'],
            'timestamp': event['timestamp'],
        }))