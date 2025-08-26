import json

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from core.users.models import User


class RefreshTokenViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.refresh_url = reverse("auth:refresh-token")
        self.user = User.objects.create_user(
            username="testrefreshuser",
            email="refresh@example.com",
            password="StrongPassword123",  # noqa: S106
            is_active=True,
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.valid_payload = {"refresh": str(self.refresh)}

    def test_refresh_token_success(self):
        """Test successful token refresh"""
        response = self.client.post(
            self.refresh_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.json()
        assert "refresh" in response.json()

    def test_refresh_token_invalid(self):
        """Test refresh with invalid token"""
        invalid_payload = {"refresh": "invalid-token"}

        response = self.client.post(
            self.refresh_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.json()

    def test_refresh_token_missing_field(self):
        """Test refresh with missing required field"""
        invalid_payload = {}

        response = self.client.post(
            self.refresh_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "refresh" in response.json()  # Field validation error
