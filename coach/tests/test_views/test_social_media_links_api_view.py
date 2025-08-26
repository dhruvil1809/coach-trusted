import uuid

import pytest
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from coach.models import Coach
from coach.models import SocialMediaLink
from coach.tests.factories import CoachFactory
from core.users.tests.factories import UserFactory


@pytest.mark.django_db
class CoachSocialMediaLinksAPIViewTestCase(TestCase):
    """
    Test cases for the CoachSocialMediaLinksRetrieveUpdateAPIView.
    """

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create users
        self.coach_user = UserFactory()
        self.other_user = UserFactory()

        # Create a coach
        self.coach = CoachFactory(user=self.coach_user)

        # URL for accessing the coach's social media links
        self.social_media_url = reverse(
            "coach:social-media-links",
            kwargs={"coach_uuid": self.coach.uuid},
        )

    def test_get_social_media_links_success(self):
        """Test getting social media links for a coach (creates if doesn't exist)."""
        response = self.client.get(self.social_media_url)

        assert response.status_code == status.HTTP_200_OK

        # Parse response data
        data = response.json()

        # Check that all expected fields are present
        expected_fields = [
            "uuid",
            "instagram",
            "facebook",
            "linkedin",
            "youtube",
            "tiktok",
            "x",
            "trustpilot",
            "google",
            "provexpert",
        ]
        for field in expected_fields:
            assert field in data

        # Verify that a SocialMediaLink was created
        assert SocialMediaLink.objects.filter(coach=self.coach).exists()

    def test_get_social_media_links_with_existing_data(self):
        """Test getting social media links when they already exist."""
        # Create social media links first
        social_media_link = SocialMediaLink.objects.create(
            coach=self.coach,
            instagram="https://instagram.com/testcoach",
            facebook="https://facebook.com/testcoach",
        )

        response = self.client.get(self.social_media_url)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["uuid"] == str(social_media_link.uuid)
        assert data["instagram"] == "https://instagram.com/testcoach"
        assert data["facebook"] == "https://facebook.com/testcoach"

    def test_update_social_media_links_authenticated_owner(self):
        """Test updating social media links as the coach owner."""
        # Login as the coach owner
        self.client.force_login(self.coach_user)

        update_data = {
            "instagram": "https://instagram.com/updated",
            "facebook": "https://facebook.com/updated",
            "linkedin": "https://linkedin.com/in/updated",
        }

        response = self.client.patch(
            self.social_media_url,
            data=update_data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify the data was updated
        social_media_link = SocialMediaLink.objects.get(coach=self.coach)
        assert social_media_link.instagram == "https://instagram.com/updated"
        assert social_media_link.facebook == "https://facebook.com/updated"
        assert social_media_link.linkedin == "https://linkedin.com/in/updated"

    def test_update_social_media_links_unauthenticated(self):
        """Test updating social media links without authentication."""
        update_data = {
            "instagram": "https://instagram.com/updated",
        }

        response = self.client.patch(
            self.social_media_url,
            data=update_data,
            content_type="application/json",
        )

        # DRF may return 403 instead of 401 in some cases
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_update_social_media_links_not_owner(self):
        """Test updating social media links as a different user."""
        # Login as a different user
        self.client.force_login(self.other_user)

        update_data = {
            "instagram": "https://instagram.com/updated",
        }

        response = self.client.patch(
            self.social_media_url,
            data=update_data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "permission" in response.json()["detail"].lower()

    def test_invalid_uuid_format(self):
        """Test providing an invalid UUID format."""
        invalid_url = reverse(
            "coach:social-media-links",
            kwargs={"coach_uuid": "not-a-uuid"},
        )
        response = self.client.get(invalid_url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_nonexistent_coach(self):
        """Test retrieving social media links for a non-existent coach."""
        random_uuid = uuid.uuid4()
        url = reverse(
            "coach:social-media-links",
            kwargs={"coach_uuid": random_uuid},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unapproved_coach_get_request(self):
        """Test retrieving social media links for an unapproved coach (GET request)."""
        # Create an unapproved coach
        unapproved_coach = CoachFactory(review_status=Coach.REVIEW_PENDING)

        url = reverse(
            "coach:social-media-links",
            kwargs={"coach_uuid": unapproved_coach.uuid},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_with_invalid_urls(self):
        """Test updating with invalid URL formats."""
        self.client.force_login(self.coach_user)

        update_data = {
            "instagram": "not-a-valid-url",
        }

        response = self.client.patch(
            self.social_media_url,
            data=update_data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "instagram" in response.json()

    def test_update_with_empty_fields(self):
        """Test updating with empty/blank fields."""
        self.client.force_login(self.coach_user)

        # First create some data
        SocialMediaLink.objects.create(
            coach=self.coach,
            instagram="https://instagram.com/testcoach",
            facebook="https://facebook.com/testcoach",
        )

        # Now clear some fields
        update_data = {
            "instagram": "",
            "facebook": "",
        }

        response = self.client.patch(
            self.social_media_url,
            data=update_data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify the fields were cleared
        social_media_link = SocialMediaLink.objects.get(coach=self.coach)
        assert social_media_link.instagram == ""
        assert social_media_link.facebook == ""
