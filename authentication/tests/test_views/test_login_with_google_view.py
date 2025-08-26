import json
from unittest.mock import patch

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.users.models import User


class LoginWithGoogleViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_google_url = reverse("auth:login-google")
        self.valid_token = "valid_google_token"  # noqa: S105
        self.mock_user_info = {
            "email": "google_user@example.com",
            "first_name": "Google",
            "last_name": "User",
        }

    @patch("authentication.firebase.validate_token")
    @patch("authentication.firebase.get_user_info")
    def test_login_google_success_new_user(
        self,
        mock_get_user_info,
        mock_validate_token,
    ):
        """Test successful Google login for a new user"""
        # Configure mocks
        mock_validate_token.return_value = True
        mock_get_user_info.return_value = self.mock_user_info

        # Send request
        payload = {"token": self.valid_token}
        response = self.client.post(
            self.login_google_url,
            json.dumps(payload),
            content_type="application/json",
        )

        # Assertions
        mock_validate_token.assert_called_once_with(self.valid_token)
        mock_get_user_info.assert_called_once_with(self.valid_token)

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.json()
        assert "refresh" in response.json()

        # Verify user was created and is active
        user = User.objects.get(email=self.mock_user_info["email"])
        assert user is not None
        assert user.is_active
        assert user.first_name == self.mock_user_info["first_name"]
        assert user.last_name == self.mock_user_info["last_name"]
        assert user.username.startswith(self.mock_user_info["email"])

    @patch("authentication.firebase.validate_token")
    @patch("authentication.firebase.get_user_info")
    def test_login_google_success_existing_user(
        self,
        mock_get_user_info,
        mock_validate_token,
    ):
        """Test successful Google login for an existing user"""
        # Create existing user
        existing_user = User.objects.create_user(
            username=f"{self.mock_user_info['email']}_abcde",
            email=self.mock_user_info["email"],
            first_name=self.mock_user_info["first_name"],
            last_name=self.mock_user_info["last_name"],
            is_active=True,
        )

        # Configure mocks
        mock_validate_token.return_value = True
        mock_get_user_info.return_value = self.mock_user_info

        # Send request
        payload = {"token": self.valid_token}
        response = self.client.post(
            self.login_google_url,
            json.dumps(payload),
            content_type="application/json",
        )

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.json()
        assert "refresh" in response.json()

        # Verify user count hasn't changed (no new users created)
        assert User.objects.count() == 1
        existing_user.refresh_from_db()
        assert existing_user.is_active

    @patch("authentication.firebase.validate_token")
    @patch("authentication.firebase.get_user_info")
    def test_login_google_inactive_user(self, mock_get_user_info, mock_validate_token):
        """Test Google login activates an inactive user"""
        # Create inactive user
        User.objects.create_user(
            username=f"{self.mock_user_info['email']}_abcde",
            email=self.mock_user_info["email"],
            first_name=self.mock_user_info["first_name"],
            last_name=self.mock_user_info["last_name"],
            is_active=False,
        )

        # Configure mocks
        mock_validate_token.return_value = True
        mock_get_user_info.return_value = self.mock_user_info

        # Send request
        payload = {"token": self.valid_token}
        response = self.client.post(
            self.login_google_url,
            json.dumps(payload),
            content_type="application/json",
        )

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.json()
        assert "refresh" in response.json()

        # Verify user is now active
        user = User.objects.get(email=self.mock_user_info["email"])
        assert user.is_active

    @patch(
        "authentication.firebase.validate_token",
        side_effect=Exception("Invalid token"),
    )
    def test_login_google_invalid_token(self, mock_validate_token):
        """Test Google login with invalid token"""
        # Send request with invalid token
        payload = {"token": "invalid_token"}
        response = self.client.post(
            self.login_google_url,
            json.dumps(payload),
            content_type="application/json",
        )

        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" in response.json() or "non_field_errors" in response.json()

    def test_login_google_missing_token(self):
        """Test Google login with missing token"""
        # Send request without token
        payload = {}
        response = self.client.post(
            self.login_google_url,
            json.dumps(payload),
            content_type="application/json",
        )

        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" in response.json()
