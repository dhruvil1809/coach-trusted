import json
from datetime import timedelta
from unittest.mock import patch

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from core.users.models import User
from core.users.models import VerificationCode


class ResendVerificationCodeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.resend_url = reverse("auth:resend-verification-code")

        # Create an inactive user
        self.inactive_user = User.objects.create_user(
            username="inactive_user",
            email="inactive@example.com",
            password="TestPassword123",  # noqa: S106
            is_active=False,
        )

        # Create an active user
        self.active_user = User.objects.create_user(
            username="active_user",
            email="active@example.com",
            password="TestPassword123",  # noqa: S106
            is_active=True,
        )

    @patch("authentication.views.User.send_verification_code")
    def test_resend_verification_code_success(self, mock_send_code):
        """Test successful verification code resend for inactive user"""
        payload = {"email": self.inactive_user.email}

        response = self.client.post(
            self.resend_url,
            json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"detail": "Verification code sent to email"}
        mock_send_code.assert_called_once()

    def test_resend_verification_code_user_not_found(self):
        """Test resend verification code for non-existent user"""
        payload = {"email": "nonexistent@example.com"}

        response = self.client.post(
            self.resend_url,
            json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User not found" in str(response.json())

    def test_resend_verification_code_user_already_active(self):
        """Test resend verification code for already active user"""
        payload = {"email": self.active_user.email}

        response = self.client.post(
            self.resend_url,
            json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User account is already active" in str(response.json())

    def test_resend_verification_code_missing_email(self):
        """Test resend verification code with missing email field"""
        payload = {}

        response = self.client.post(
            self.resend_url,
            json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()

    def test_resend_verification_code_invalid_email(self):
        """Test resend verification code with invalid email format"""
        payload = {"email": "invalid-email"}

        response = self.client.post(
            self.resend_url,
            json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()

    def test_resend_verification_code_invalidates_old_codes(self):
        """Test that resending invalidates old verification codes"""
        # Create an initial verification code with older timestamp to avoid rate limiting  # noqa: E501
        old_code = VerificationCode.objects.create(user=self.inactive_user)
        old_code_value = old_code.code

        # Move the old code's created_at back by 2 minutes to avoid rate limiting
        old_code.created_at = timezone.now() - timezone.timedelta(minutes=2)
        old_code.save()

        payload = {"email": self.inactive_user.email}

        response = self.client.post(
            self.resend_url,
            json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify old code is deleted and new code exists
        assert not VerificationCode.objects.filter(code=old_code_value).exists()
        assert VerificationCode.objects.filter(user=self.inactive_user).count() == 1

        # Verify the new code is different
        new_code = VerificationCode.objects.filter(user=self.inactive_user).first()
        assert new_code.code != old_code_value

    def test_resend_verification_code_rate_limiting(self):
        """Test rate limiting prevents frequent requests"""
        # First request should succeed
        payload = {"email": self.inactive_user.email}

        response = self.client.post(
            self.resend_url,
            json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        # Immediate second request should be rate limited
        response = self.client.post(
            self.resend_url,
            json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Please wait before requesting" in response.json()["error"]

    def test_resend_verification_code_rate_limiting_expires(self):
        """Test rate limiting expires after time period"""
        payload = {"email": self.inactive_user.email}

        # First request
        response = self.client.post(
            self.resend_url,
            json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        # Manually update the verification code timestamp to be older
        code = VerificationCode.objects.filter(user=self.inactive_user).first()
        code.created_at = timezone.now() - timedelta(minutes=2)
        code.save()

        # Second request should now succeed
        response = self.client.post(
            self.resend_url,
            json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_resend_verification_code_case_insensitive_email(self):
        """Test resend verification code with case insensitive email"""
        payload = {"email": self.inactive_user.email.upper()}

        with patch("authentication.views.User.send_verification_code"):
            response = self.client.post(
                self.resend_url,
                json.dumps(payload),
                content_type="application/json",
            )

        # Should work with uppercase email since Django's EmailField handles this
        assert response.status_code == status.HTTP_200_OK

    def test_resend_verification_code_only_one_active_code(self):
        """Test that only one verification code exists per user at any time"""
        # Send verification code twice
        payload = {"email": self.inactive_user.email}

        # First request
        self.client.post(
            self.resend_url,
            json.dumps(payload),
            content_type="application/json",
        )

        # Wait to avoid rate limiting
        code = VerificationCode.objects.filter(user=self.inactive_user).first()
        code.created_at = timezone.now() - timedelta(minutes=2)
        code.save()

        # Second request
        self.client.post(
            self.resend_url,
            json.dumps(payload),
            content_type="application/json",
        )

        # Should only have one verification code
        assert VerificationCode.objects.filter(user=self.inactive_user).count() == 1
