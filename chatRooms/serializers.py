# chat_rooms/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage, ChatRoomMember, MessageReaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email']

class MessageReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = MessageReaction
        fields = ['id', 'reaction', 'user', 'created_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    mentioned_users = UserSerializer(many=True, read_only=True)
    reply_to_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'sender', 'sender_name', 'content', 'timestamp',
            'is_edited', 'edited_at', 'reactions', 'reply_to',
            'reply_to_message', 'mentioned_users'
        ]

    def get_reply_to_message(self, obj):
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'content': obj.reply_to.content,
                'sender_name': obj.reply_to.sender.username
            }
        return None

class ChatRoomMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ChatRoomMember
        fields = ['user', 'role', 'joined_at', 'is_muted', 'last_seen', 'is_typing']

class ChatRoomSerializer(serializers.ModelSerializer):
    participant_count = serializers.SerializerMethodField()
    members = ChatRoomMemberSerializer(source='chatroommmember_set', many=True, read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'description', 'created_at', 'created_by',
            'participant_count', 'is_active', 'is_private',
            'max_participants', 'last_activity', 'members'
        ]

    def get_participant_count(self, obj):
        return obj.participants.count()
