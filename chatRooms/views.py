# chat_rooms/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import ChatRoom, ChatMessage, ChatRoomMember, MessageReaction
from .serializers import (
    ChatRoomSerializer, ChatMessageSerializer,
    ChatRoomMemberSerializer, MessageReactionSerializer
)

class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            Q(is_private=False) | Q(participants=user)
        ).distinct()

    def perform_create(self, serializer):
        chat_room = serializer.save(created_by=self.request.user)
        ChatRoomMember.objects.create(
            user=self.request.user,
            chat_room=chat_room,
            role='admin'
        )

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        chat_room = self.get_object()
        
        if not chat_room.can_join(request.user):
            return Response(
                {'error': 'Cannot join this room'},
                status=status.HTTP_403_FORBIDDEN
            )

        ChatRoomMember.objects.create(
            user=request.user,
            chat_room=chat_room
        )
        return Response({'status': 'joined'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        chat_room = self.get_object()
        ChatRoomMember.objects.filter(
            user=request.user,
            chat_room=chat_room
        ).delete()
        return Response({'status': 'left'})

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chat_room = self.get_object()
        page = self.paginate_queryset(
            ChatMessage.objects.filter(room=chat_room)
        )
        serializer = ChatMessageSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_reaction(self, request, pk=None):
        message_id = request.data.get('message_id')
        reaction = request.data.get('reaction')
        
        try:
            message = ChatMessage.objects.get(id=message_id, room_id=pk)
            MessageReaction.objects.create(
                message=message,
                user=request.user,
                reaction=reaction
            )
            return Response({'status': 'reaction_added'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )