from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    verification_token = models.CharField(max_length=36, blank=True, null=True)  # Store verification token
    is_verified = models.BooleanField(default=False)  # Track if email is verified

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
