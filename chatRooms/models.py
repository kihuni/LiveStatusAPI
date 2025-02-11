# chat_rooms/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='chat_rooms',
        through='ChatRoomMember'
    )
    is_active = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=50)
    is_private = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def is_participant(self, user):
        return self.participants.filter(id=user.id).exists()

    def can_join(self, user):
        return (
            self.is_active and
            not self.is_private and
            self.participants.count() < self.max_participants
        )

class ChatRoomMember(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_muted = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    is_typing = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'chat_room')

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    reply_to = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replies'
    )
    mentioned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='mentions',
        blank=True
    )

    class Meta:
        ordering = ['timestamp']

    def edit_message(self, new_content):
        self.content = new_content
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save()

class MessageReaction(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=50)  # Store emoji or reaction type
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user', 'reaction')