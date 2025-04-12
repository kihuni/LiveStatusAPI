# users/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
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
    
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']

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
