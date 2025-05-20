# users/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from presence.models import Presence
import re
from uuid import uuid4

User = get_user_model()


def get_device_type(user_agent: str) -> str:
    """
    Parse the User-Agent header to determine the device type.
    """
    if not user_agent:
        return "unknown"

    user_agent = user_agent.lower()
    if re.search(r"mobile|android|iphone|ipad|ipod|opera mini|webos|blackberry|windows phone", user_agent):
        return "mobile"
    elif re.search(r"tablet|kindle|nexus 7|ipad", user_agent):
        return "tablet"
    elif re.search(r"windows|macintosh|linux|x11|postmanruntime", user_agent):
        return "desktop"
    elif re.search(r"bot|crawl|spider|slurp", user_agent):
        return "bot"
    return "unknown"

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ["email", "username", "password"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("A user with this email already exists."))
        return value

    def validate_username(self, value):
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError(_("Username can only contain letters, numbers, and underscores."))
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(_("A user with this username already exists."))
        return value

    def validate_password(self, value):
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(_("Password must contain at least one uppercase letter."))
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError(_("Password must contain at least one number."))
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError(_("Password must contain at least one special character."))
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            is_active=False,
        )

        user.verification_token = uuid4()
        user.save(update_fields=["verification_token"])

        verification_url = self.context["request"].build_absolute_uri(
            reverse("verify-email", kwargs={"token": str(user.verification_token)})
        )
        subject = _("Verify Your Email Address")
        message = _("Click the link to verify your email: {url}").format(url=verification_url)
        send_mail(
            subject,
            message,
            None,  # Use DEFAULT_FROM_EMAIL from settings
            [user.email],
            fail_silently=False,
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)  # Remove username field if present

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not (email and password):
            raise serializers.ValidationError(_("Must include 'email' and 'password'."))

        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            raise serializers.ValidationError(_("Invalid email or password."))
        if not user.is_verified:
            raise serializers.ValidationError(_("Please verify your email before logging in."))
        if not user.is_active:
            raise serializers.ValidationError(_("User account is inactive."))

        self.user = user
        refresh = self.get_token(self.user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(self.user.id),
                "email": self.user.email,
                "username": self.user.username,
                "engagement_score": self.user.engagement_score,
            },
        }

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("No user is associated with this email."))
        return value

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
        token = PasswordResetTokenGenerator().make_token(user)

        reset_url = self.context["request"].build_absolute_uri(
            reverse("password-reset-confirm", kwargs={"uidb64": uid, "token": token})
        )
        subject = _("Reset Your Password")
        message = _("Click the link to reset your password: {url}").format(url=reset_url)
        send_mail(
            subject,
            message,
            None,  # Use DEFAULT_FROM_EMAIL from settings
            [user.email],
            fail_silently=False,
        )

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate_new_password(self, value):
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(_("Password must contain at least one uppercase letter."))
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError(_("Password must contain at least one number."))
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError(_("Password must contain at least one special character."))
        return value

    def validate(self, attrs):
        uidb64 = self.context.get("uidb64")
        token = self.context.get("token")
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError(_("Invalid reset link."))

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError(_("Invalid or expired reset token."))

        self.user = user
        return attrs

    def save(self):
        password = self.validated_data["new_password"]
        self.user.set_password(password)
        self.user.save()
        # Optionally invalidate existing tokens
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
        OutstandingToken.objects.filter(user=self.user).delete()