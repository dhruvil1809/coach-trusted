import json
from unittest.mock import patch

import pytest
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.users.models import Profile
from core.users.models import User


class RegisterViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("auth:register")
        self.valid_payload = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "country_code": "US",
            "phone_number": "+1234567890",
            "password": "StrongPassword123",
        }

    def test_register_success(self):
        """Test successful user registration"""
        response = self.client.post(
            self.register_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"detail": "Verification code sent to email"}

        # Verify user was created but not active
        user = User.objects.filter(email=self.valid_payload["email"]).first()
        assert user is not None
        assert not user.is_active
        assert user.first_name == self.valid_payload["first_name"]
        assert user.last_name == self.valid_payload["last_name"]
        assert user.phone_number == self.valid_payload["phone_number"]

        # Verify username was generated correctly (email + random string)
        assert user.username.startswith(self.valid_payload["email"])

        # Verify profile was created
        profile = Profile.objects.filter(user=user).first()
        assert profile is not None
        assert profile.first_name == self.valid_payload["first_name"]
        assert profile.last_name == self.valid_payload["last_name"]
        assert profile.email == self.valid_payload["email"]
        assert profile.country_code == self.valid_payload["country_code"]
        assert profile.phone_number == self.valid_payload["phone_number"]

        # Verify verification code was sent (user has at least one verification code)
        assert user.verification_codes.exists()

    def test_register_missing_fields(self):
        """Test registration with missing required fields"""
        invalid_payload = {"email": "incomplete@example.com"}

        response = self.client.post(
            self.register_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.json()  # Password field should be required

    def test_register_missing_country_code(self):
        """Test registration with missing country_code field"""
        invalid_payload = self.valid_payload.copy()
        del invalid_payload["country_code"]

        response = self.client.post(
            self.register_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Country code field should be required
        assert "country_code" in response.json()

    def test_register_existing_email(self):
        """Test registration with an email that already exists"""
        # First create a user with the email
        User.objects.create_user(
            username="existinguser",
            email=self.valid_payload["email"],
            password="password123",  # noqa: S106
        )

        # Then try to register with the same email
        response = self.client.post(
            self.register_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()  # Email validation error

    def test_register_password_validation(self):
        """Test registration with an invalid password"""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["password"] = "short"  # Too short password  # noqa: S105

        response = self.client.post(
            self.register_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.json()

    def test_transaction_atomicity_on_profile_creation_failure(self):
        """Test that user is not created if profile creation fails"""
        # Mock Profile.objects.create to raise an exception
        with patch("core.users.models.Profile.objects.create") as mock_create:
            mock_create.side_effect = ValueError("Profile creation failed")

            initial_user_count = User.objects.count()
            initial_profile_count = Profile.objects.count()

            # The request should fail due to the exception in the atomic block
            with pytest.raises(ValueError, match="Profile creation failed"):
                self.client.post(
                    self.register_url,
                    json.dumps(self.valid_payload),
                    content_type="application/json",
                )

            # Neither user nor profile should be created due to transaction rollback
            assert User.objects.count() == initial_user_count
            assert Profile.objects.count() == initial_profile_count

            # Verify no user with the email exists
            assert not User.objects.filter(email=self.valid_payload["email"]).exists()

    def test_transaction_atomicity_on_verification_email_failure(self):
        """Test that user creation is rolled back if verification email fails"""
        # Mock send_verification_code to raise an exception
        with patch("core.users.models.User.send_verification_code") as mock_send:
            mock_send.side_effect = RuntimeError("Email sending failed")

            initial_user_count = User.objects.count()
            initial_profile_count = Profile.objects.count()

            # The request should fail due to the exception in the atomic block
            with pytest.raises(RuntimeError, match="Email sending failed"):
                self.client.post(
                    self.register_url,
                    json.dumps(self.valid_payload),
                    content_type="application/json",
                )

            # Neither user nor profile should be created due to transaction rollback
            assert User.objects.count() == initial_user_count
            assert Profile.objects.count() == initial_profile_count

            # Verify no user with the email exists
            assert not User.objects.filter(email=self.valid_payload["email"]).exists()
