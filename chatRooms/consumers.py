# ASGI WebSocket consumer for chat rooms

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage
import json

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Send user join notification
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'user': self.scope['user'].username
            }
        )
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        message_type = content.get('type', 'message')
        
        if message_type == 'message':
            await self.save_message(content)
        elif message_type == 'typing':
            await self.broadcast_typing_status(content)
    
    @database_sync_to_async
    def save_message(self, content):
        message = ChatMessage.objects.create(
            room_id=self.room_id,
            sender=self.scope['user'],
            content=content['message']
        )
        return message
