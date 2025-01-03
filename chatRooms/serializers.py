# chat_rooms/serializers.py
from rest_framework import serializers
from .models import ChatRoom, ChatMessage, ChatRoomMember

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'sender_name', 'content', 'timestamp', 'is_edited', 'edited_at']

class ChatRoomSerializer(serializers.ModelSerializer):
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'description', 'created_at', 'created_by', 'participant_count', 'is_active']
    
    def get_participant_count(self, obj):
        return obj.participants.count()