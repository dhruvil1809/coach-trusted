import json

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.users.models import User
from core.users.models import VerificationCode


class RegisterConfirmationViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.confirm_url = reverse("auth:register-confirmation")
        self.user = User.objects.create_user(
            username="testuser_register_confirm",
            email="register_confirm@example.com",
            password="StrongPassword123",  # noqa: S106
            is_active=False,
        )
        self.user.send_verification_code()
        self.verification_code = VerificationCode.objects.last().code
        self.valid_payload = {
            "email": self.user.email,
            "code": self.verification_code,
        }

    def test_confirm_registration_success(self):
        """Test successful registration confirmation"""
        response = self.client.post(
            self.confirm_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.json()
        assert "refresh" in response.json()

        # Verify user is now active
        self.user.refresh_from_db()
        assert self.user.is_active

    def test_confirm_registration_invalid_code(self):
        """Test confirmation with invalid verification code"""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["code"] = "wrong_code"

        response = self.client.post(
            self.confirm_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid verification code" in str(response.json())

        # Verify user is still inactive
        self.user.refresh_from_db()
        assert not self.user.is_active

    def test_confirm_registration_missing_fields(self):
        """Test confirmation with missing required fields"""
        invalid_payload = {"email": self.user.email}  # Missing code field

        response = self.client.post(
            self.confirm_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "code" in response.json()

    def test_confirm_registration_user_not_found(self):
        """Test confirmation for non-existent user"""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["email"] = "nonexistent@example.com"

        response = self.client.post(
            self.confirm_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User not found" in str(response.json())

    def test_confirm_registration_already_active(self):
        """Test confirmation for already active user"""
        self.user.is_active = True
        self.user.save()

        response = self.client.post(
            self.confirm_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User already registered" in str(response.json())
