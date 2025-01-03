from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer

class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        chat_room = serializer.save(created_by=self.request.user)
        chat_room.participants.add(self.request.user)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        chat_room = self.get_object()
        chat_room.participants.add(request.user)
        return Response({'status': 'joined'})
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        chat_room = self.get_object()
        chat_room.participants.remove(request.user)
        return Response({'status': 'left'})
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chat_room = self.get_object()
        messages = ChatMessage.objects.filter(room=chat_room)
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
