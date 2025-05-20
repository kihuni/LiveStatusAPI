# users/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True"))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model using email as the unique identifier, with support for
    presence tracking and engagement analytics.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    email = models.EmailField(
        unique=True,
        max_length=255,
        error_messages={"unique": _("A user with that email already exists.")},
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_("Optional username for display purposes."),
    )
    verification_token = models.UUIDField(
        default=uuid.uuid4,
        blank=True,
        null=True,
        db_index=True,
        help_text=_("Token for email verification."),
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=_("Indicates whether the user's email is verified."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this user account is active."),
    )
    is_staff = models.BooleanField(
        default=False,
        help_text=_("Designates whether the user can access the admin site."),
    )
    engagement_score = models.FloatField(
        default=0.0,
        help_text=_("Score representing user engagement based on activity."),
    )
    last_presence_update = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp of the last presence update."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Timestamp when the user was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Timestamp when the user was last updated."),
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "custom_user"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["verification_token"]),
        ]
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """
        Override save to ensure verification_token is regenerated if needed.
        """
        if not self.is_verified and not self.verification_token:
            self.verification_token = uuid.uuid4()
        super().save(*args, **kwargs)