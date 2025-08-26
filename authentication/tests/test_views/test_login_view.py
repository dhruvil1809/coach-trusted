import json

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.users.models import User


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("auth:login")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password",  # noqa: S106
            is_active=True,
        )

    def test_login_success(self):
        """Test login with valid credentials"""

        data = {"email": "test@example.com", "password": "password"}
        response = self.client.post(
            self.login_url,
            json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.json()
        assert "refresh" in response.json()

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""

        data = {"email": "invalid@example.com", "password": "wrongpassword"}
        response = self.client.post(
            self.login_url,
            json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_missing_fields(self):
        """Test login with missing required fields"""

        data = {"email": "testuser"}
        response = self.client.post(
            self.login_url,
            json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_inactive_user(self):
        """Test login with inactive user"""

        # Create an inactive user
        User.objects.create_user(
            username="inactiveuser",
            email="inactive@example.com",
            password="password",  # noqa: S106
            is_active=False,
        )

        # Attempt to login with inactive user credentials
        data = {"email": "inactive@example.com", "password": "password"}
        response = self.client.post(
            self.login_url,
            json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Account not activated" in response.json()["error"]
