# chat_rooms/consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage, ChatRoomMember
import json

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Verify user has access to the room
        if not await self.can_access_room():
            await self.close()
            return

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
                'user': self.user.username
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Send user leave notification
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user': self.user.username
                }
            )
            
            # Update last seen
            await self.update_last_seen()

            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive_json(self, content):
        message_type = content.get('type', 'message')
        
        handlers = {
            'message': self.handle_message,
            'typing': self.handle_typing,
            'reaction': self.handle_reaction,
            'edit': self.handle_edit,
        }
        
        handler = handlers.get(message_type)
        if handler:
            await handler(content)

    async def handle_message(self, content):
        message = await self.save_message(content)
        
        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'sender': self.user.username,
                    'content': content['message'],
                    'timestamp': message.timestamp.isoformat(),
                }
            }
        )

    async def handle_typing(self, content):
        await self.update_typing_status(content.get('typing', False))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_status',
                'user': self.user.username,
                'typing': content.get('typing', False)
            }
        )

    async def handle_reaction(self, content):
        await self.save_reaction(content)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_reaction',
                'message_id': content['message_id'],
                'reaction': content['reaction'],
                'user': self.user.username
            }
        )

    async def handle_edit(self, content):
        success = await self.edit_message(content)
        if success:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_edited',
                    'message_id': content['message_id'],
                    'new_content': content['new_content']
                }
            )

    # Helper methods
    @database_sync_to_async
    def can_access_room(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.is_participant(self.user)
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        return ChatMessage.objects.create(
            room_id=self.room_id,
            sender=self.user,
            content=content['message'],
            reply_to_id=content.get('reply_to')
        )

    @database_sync_to_async
    def update_typing_status(self, is_typing):
        ChatRoomMember.objects.filter(
            chat_room_id=self.room_id,
            user=self.user
        ).update(is_typing=is_typing)

    @database_sync_to_async
    def update_last_seen(self):
        ChatRoomMember.objects.filter(
            chat_room_id=self.room_id,
            user=self.user
        ).update(last_seen=timezone.now())

    @database_sync_to_async
    def save_reaction(self, content):
        message = ChatMessage.objects.get(id=content['message_id'])
        MessageReaction.objects.create(
            message=message,
            user=self.user,
            reaction=content['reaction']
        )

    @database_sync_to_async
    def edit_message(self, content):
        try:
            message = ChatMessage.objects.get(
                id=content['message_id'],
                sender=self.user
            )
            message.edit_message(content['new_content'])
            return True
        except ChatMessage.DoesNotExist:
            return False