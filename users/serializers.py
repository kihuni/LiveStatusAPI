from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
import uuid

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_email(self, value):
        # Check if email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # Create the user with is_active=False until email is verified
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False  # User cannot log in until email is verified
        )

        # Generate a verification token (you can use UUID or a more secure token)
        verification_token = str(uuid.uuid4())
        user.verification_token = verification_token  # Add a field to CustomUser for this (see below)
        user.save()

        # Send email verification link
        verification_url = self.context['request'].build_absolute_uri(
            reverse('verify-email', kwargs={'token': verification_token})
        )
        subject = 'Verify Your Email Address'
        message = f'Click the link to verify your email: {verification_url}'
        send_mail(
            subject,
            message,
            'from@example.com',  # Replace with your DEFAULT_FROM_EMAIL
            [user.email],
            fail_silently=False,
        )

        return user
    
