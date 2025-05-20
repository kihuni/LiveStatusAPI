# users/views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from presence.models import Presence
from users.serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
import logging

# Set up logging
logger = logging.getLogger(__name__)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Register a new user and send an email verification link.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_scope = "register"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info(f"User registered: {user.email}")
        # Trigger webhook for user registration
        from webhooks.tasks import trigger_webhook
        trigger_webhook.delay(user_id=str(user.id), event="user.registered")
        return Response(
            {
                "message": _("User registered successfully. Please verify your email to activate your account."),
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                },
            },
            status=status.HTTP_201_CREATED,
        )

class VerifyEmailView(generics.GenericAPIView):
    """
    Verify a user's email address using a token.
    """
    permission_classes = [AllowAny]
    throttle_scope = "verify_email"

    def get(self, request, token, *args, **kwargs):
        try:
            user = User.objects.get(verification_token=token)
            if user.is_verified:
                return Response(
                    {"message": _("Email already verified.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.is_verified = True
            user.is_active = True
            user.verification_token = None
            user.save(update_fields=["is_verified", "is_active", "verification_token"])
            logger.info(f"Email verified for user: {user.email}")
            # Trigger webhook for email verification
            from webhooks.tasks import trigger_webhook
            trigger_webhook.delay(user_id=str(user.id), event="user.email_verified")
            return Response(
                {"message": _("Email verified successfully. You can now log in.")},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": _("Invalid verification token.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Authenticate a user and return JWT tokens with user details.
    """
    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = User.objects.get(email=request.data.get("email"))
        logger.info(f"User logged in: {user.email}")
        # Trigger webhook for login
        from webhooks.tasks import trigger_webhook
        trigger_webhook.delay(user_id=str(user.id), event="user.logged_in")
        return response

class PasswordResetRequestView(generics.GenericAPIView):
    """
    Request a password reset link via email.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    throttle_scope = "password_reset"

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.get(email=serializer.validated_data["email"])
        logger.info(f"Password reset requested for user: {user.email}")
        # Trigger webhook for password reset request
        from webhooks.tasks import trigger_webhook
        trigger_webhook.delay(user_id=str(user.id), event="user.password_reset_requested")
        return Response(
            {"message": _("Password reset link sent.")},
            status=status.HTTP_200_OK,
        )

class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Confirm a password reset using a token and set a new password.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    throttle_scope = "password_reset_confirm"

    def post(self, request, uidb64, token):
        serializer = self.get_serializer(data=request.data, context={"uidb64": uidb64, "token": token})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"Password reset for user: {serializer.user.email}")
        # Trigger webhook for password reset
        from webhooks.tasks import trigger_webhook
        trigger_webhook.delay(user_id=str(serializer.user.id), event="user.password_reset")
        return Response(
            {"message": _("Password has been reset successfully.")},
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "logout"

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": _("Refresh token is required.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Update the latest Presence record to offline
            presence = Presence.objects.filter(user=request.user).order_by("-last_seen").first()
            if presence:
                presence.status = "offline"
                presence.save()  # This triggers the WebSocket broadcast via the signal
                request.user.last_presence_update = presence.last_seen
                request.user.save(update_fields=["last_presence_update"])

            logger.info(f"User logged out: {request.user.email}")
            return Response(
                {"detail": _("Successfully logged out.")},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            logger.error(f"Logout failed for user {request.user.email}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )