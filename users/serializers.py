# users/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import reset_password_token
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from django.contrib.auth import get_user_model
from presence.models import Presence, PresenceRecord
from django.core.mail import send_mail
from django.urls import reverse
import uuid
import re  


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

    def get_device_type(self, user_agent):
        """Parse the User-Agent header to determine the device type."""
        if not user_agent:
            return "unknown"

        user_agent = user_agent.lower()
        # Check for mobile devices
        if re.search(r"mobile|android|iphone|ipad|ipod|opera mini|webos|blackberry|windows phone", user_agent):
            return "mobile"
        # Check for tablets
        elif re.search(r"tablet|kindle|nexus 7|ipad", user_agent):
            return "tablet"
        # Check for desktops (including Postman)
        elif re.search(r"windows|macintosh|linux|x11|postmanruntime", user_agent):
            return "desktop"
        # Check for bots or other clients
        elif re.search(r"bot|crawl|spider|slurp", user_agent):
            return "bot"
        return "unknown"

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False
        )

        user_agent = self.context['request'].META.get('HTTP_USER_AGENT', '')
        device_type = self.get_device_type(user_agent)
        Presence.objects.create(user=user, status='offline', device_type=device_type)

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
            'from@example.com',
            [user.email],
            fail_silently=False,
        )

        return user
    
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']

    def get_device_type(self, user_agent):
        """Parse the User-Agent header to determine the device type."""
        if not user_agent:
            return "unknown"

        user_agent = user_agent.lower()
        # Check for mobile devices
        if re.search(r"mobile|android|iphone|ipad|ipod|opera mini|webos|blackberry|windows phone", user_agent):
            return "mobile"
        # Check for tablets
        elif re.search(r"tablet|kindle|nexus 7|ipad", user_agent):
            return "tablet"
        # Check for desktops (including Postman)
        elif re.search(r"windows|macintosh|linux|x11|postmanruntime", user_agent):
            return "desktop"
        # Check for bots or other clients
        elif re.search(r"bot|crawl|spider|slurp", user_agent):
            return "bot"
        return "unknown"

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = User.objects.filter(email=email).first()
            if user and user.check_password(password):
                if not user.is_verified:
                    raise serializers.ValidationError("Please verify your email before logging in.")
                if not user.is_active:
                    raise serializers.ValidationError("User account is inactive.")
                
                self.user = user

                # Update the user's presence to 'online'
                presence, created = Presence.objects.get_or_create(user=self.user)
                if presence.status != 'online' or created:
                    presence.status = 'online'
                    user_agent = self.context['request'].META.get('HTTP_USER_AGENT', '')
                    presence.device_type = self.get_device_type(user_agent)
                    presence.save()

                refresh = self.get_token(self.user)
                data = {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": str(self.user.id),
                        "email": self.user.email
                    }
                }
                return data
            else:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")
        
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is associated with this email.")
        return value

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = reset_password_token.make_token(user)

        reset_url = self.context['request'].build_absolute_uri(
            reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})
        )
        subject = 'Reset Your Password'
        message = f'Click the link to reset your password: {reset_url}'

        send_mail(
            subject,
            message,
            'stephenkihuni55@gmail.com',
            [user.email],
            fail_silently=False,
        )
        
class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        uidb64 = self.context.get('uidb64')
        token = self.context.get('token')
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid reset link.")
        
        if not reset_password_token.check_token(user, token):
            raise serializers.ValidationError("Invalid or expired reset token.")
        
        self.user = user
        return attrs

    def save(self):
        password = self.validated_data['new_password']
        self.user.set_password(password)
        self.user.save()