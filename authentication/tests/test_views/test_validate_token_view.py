from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from core.users.models import User


class ValidateTokenViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.validate_url = reverse("auth:validate-token")
        self.user = User.objects.create_user(
            username="testvalidateuser",
            email="validate@example.com",
            password="StrongPassword123",  # noqa: S106
            is_active=True,
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_validate_token_success(self):
        """Test successful token validation"""
        # Set up the authorization header with the token
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {self.access_token}"

        response = self.client.post(self.validate_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"detail": "Token is valid"}

    def test_validate_token_missing(self):
        """Test validation without providing a token"""
        # No authorization header
        response = self.client.post(self.validate_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "detail" in response.json()

    def test_validate_token_invalid(self):
        """Test validation with invalid token"""
        # Set up an invalid authorization token
        self.client.defaults["HTTP_AUTHORIZATION"] = "Bearer invalid-token"

        response = self.client.post(self.validate_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "code" in response.json()
