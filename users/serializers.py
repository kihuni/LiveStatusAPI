# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
import uuid

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False
        )

        verification_token = str(uuid.uuid4())
        user.verification_token = verification_token
        user.save()

        verification_url = self.context['request'].build_absolute_uri(
            reverse('verify-email', kwargs={'token': verification_token})
        )
        subject = 'Verify Your Email Address'
        message = f'Click the link to verify your email: {verification_url}'
        send_mail(
            subject,
            message,
            'stephenkihuni55@gmail.com',
            [user.email],
            fail_silently=False,
        )

        return user
    
    

