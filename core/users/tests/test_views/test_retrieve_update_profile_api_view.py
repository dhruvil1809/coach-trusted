import json

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.users.models import Profile
from core.users.models import User


class RetrieveUpdateProfileAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile_url = reverse("users:profile")

        # Create test user with profile
        self.user = User.objects.create_user(
            username="testprofileuser",
            email="testprofile@example.com",
            password="TestPassword123",  # noqa: S106
            is_active=True,
        )

        self.profile = Profile.objects.create(
            user=self.user,
            first_name="Test",
            last_name="Profile",
            email="testprofile@example.com",
            phone_number="+1234567890",
        )

        # Create update data
        self.valid_payload = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com",
            "phone_number": "+9876543210",
        }

    def test_retrieve_profile_unauthenticated(self):
        """Test retrieving profile without authentication fails"""
        response = self.client.get(self.profile_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_profile_unauthenticated(self):
        """Test updating profile without authentication fails"""
        response = self.client.post(
            self.profile_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_profile_success(self):
        """Test successful profile retrieval"""
        # Authenticate user
        self.client.login(
            username="testprofileuser",
            password="TestPassword123",  # noqa: S106
        )

        response = self.client.get(self.profile_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["first_name"] == self.profile.first_name
        assert data["last_name"] == self.profile.last_name
        assert data["email"] == self.profile.email
        assert data["phone_number"] == self.profile.phone_number

    def test_update_profile_success(self):
        """Test successful profile update"""
        # Authenticate user
        self.client.login(
            username="testprofileuser",
            password="TestPassword123",  # noqa: S106
        )

        response = self.client.post(
            self.profile_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        # Verify profile was updated
        self.profile.refresh_from_db()
        assert self.profile.first_name == self.valid_payload["first_name"]
        assert self.profile.last_name == self.valid_payload["last_name"]
        assert self.profile.email == self.valid_payload["email"]
        assert self.profile.phone_number == self.valid_payload["phone_number"]

    def test_update_profile_invalid_data(self):
        """Test profile update with invalid data"""
        # Authenticate user
        self.client.login(
            username="testprofileuser",
            password="TestPassword123",  # noqa: S106
        )

        # Try to update with empty first name (required field)
        invalid_payload = self.valid_payload.copy()
        invalid_payload["first_name"] = ""

        response = self.client.post(
            self.profile_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "first_name" in response.json()
