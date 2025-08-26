import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

from .utils import send_verification_email


def get_profile_picture_upload_location(instance, filename):
    """Generate a unique file path for the profile picture with UUID filename."""
    ext = Path(filename).suffix  # Get file extension
    uuid_filename = f"{uuid.uuid4()}{ext}"
    return f"profile-pictures/{uuid_filename}"


class User(AbstractUser):
    """
    Default custom user model for Coach Trusted.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    phone_number = models.CharField(max_length=20, blank=True)

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def _generate_verification_code(self):
        """Generate a random verification code."""
        # Invalidate all previous verification codes for this user
        self.verification_codes.all().delete()

        # Create new verification code
        verification_code = VerificationCode.objects.create(user=self)
        return verification_code.code

    def send_verification_code(self):
        """Send verification code to user's email."""
        verification_code = self._generate_verification_code()
        send_verification_email(self.email, verification_code)

    def send_password_reset_email(self, reset_token):
        """Send password reset email to user's email."""
        # This would typically send an email with the reset token
        # For now, we'll just print it (you can implement actual email sending later)
        reset_url = f"https://your-frontend.com/reset-password?token={reset_token}"
        print(f"Password reset email sent to {self.email} with token: {reset_token}")
        print(f"Reset URL: {reset_url}")
        # TODO: Implement actual email sending
        # send_password_reset_email(self.email, reset_token)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    country_code = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(
        upload_to=get_profile_picture_upload_location,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # Update the user fields before saving the profile
        self.update_user_fields()
        super().save(*args, **kwargs)

    def update_user_fields(self):
        """
        Updates the associated User instance with the current profile information.
        This method synchronizes the User model fields with the corresponding fields
        from the profile model, ensuring consistency between the two related models.
        The synchronized fields are:
        - first_name
        - last_name
        - email
        - phone_number
        After updating the fields, the User instance is saved to the database.
        """

        self.user.first_name = self.first_name
        self.user.last_name = self.last_name
        self.user.email = self.email
        self.user.phone_number = self.phone_number
        self.user.save()


class VerificationCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification_codes",
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.code}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = get_random_string(6, "0123456789")
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if the verification code is still valid (24 hours)."""
        return self.created_at >= timezone.now() - timezone.timedelta(hours=24)


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.token[:10]}..."

    def is_valid(self):
        """Check if the password reset token is still valid (24 hours)."""
        return self.created_at >= timezone.now() - timezone.timedelta(hours=24)
