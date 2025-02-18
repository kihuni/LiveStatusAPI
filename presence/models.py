from django.db import models
from django.conf import settings


class Presence(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[
        ('online', 'Online'),
        ('away', 'Away'),
        ('offline', 'Offline'),
        ('busy', 'Busy'),
    ], default='offline')
    
    last_seen = models.DateTimeField(auto_now=True)
    
    device_type = models.CharField(max_length=10, choices=[
        ('mobile', 'Mobile'),
        ('desktop', 'Desktop'),
        ('tablet', 'Tablet'),
    ], default='desktop')