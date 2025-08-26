import json
import uuid

import pytest
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from coach.models import Coach
from coach.models import SavedCoach
from coach.tests.factories import CoachFactory
from core.users.tests.factories import UserFactory


@pytest.mark.django_db
class CreateSavedCoachAPIViewTestCase(TestCase):
    """
    Test cases for the CreateSavedCoachAPIView.
    """

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.create_saved_coach_url = reverse("coach:create-saved-coach")

        # Create users
        self.user = UserFactory()
        self.coach_user = UserFactory()

        # Create an approved coach
        self.approved_coach = CoachFactory(review_status=Coach.REVIEW_APPROVED)

        # Create an unapproved coach
        self.unapproved_coach = CoachFactory(review_status=Coach.REVIEW_PENDING)

        # Create a coach owned by the user (for testing self-save prevention)
        self.user_coach = CoachFactory(
            user=self.user,
            review_status=Coach.REVIEW_APPROVED,
        )

    def test_save_approved_coach_success(self):
        """Test successfully saving an approved coach."""
        self.client.force_login(self.user)

        payload = {"coach_uuid": str(self.approved_coach.uuid)}

        response = self.client.post(
            self.create_saved_coach_url,
            json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Verify the saved coach was created
        saved_coach = SavedCoach.objects.filter(
            user=self.user,
            coach=self.approved_coach,
        ).first()
        assert saved_coach is not None

    def test_save_unapproved_coach_fails(self):
        """Test that saving an unapproved coach fails."""
        self.client.force_login(self.user)

        payload = {"coach_uuid": str(self.unapproved_coach.uuid)}

        response = self.client.post(
            self.create_saved_coach_url,
            json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_message = "Coach with this UUID does not exist or is not available"
        assert error_message in str(response.content)

        # Verify no saved coach was created
        saved_coach = SavedCoach.objects.filter(
            user=self.user,
            coach=self.unapproved_coach,
        ).first()
        assert saved_coach is None

    def test_save_nonexistent_coach_fails(self):
        """Test that saving a non-existent coach fails."""
        self.client.force_login(self.user)

        payload = {"coach_uuid": str(uuid.uuid4())}

        response = self.client.post(
            self.create_saved_coach_url,
            json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_message = "Coach with this UUID does not exist or is not available"
        assert error_message in str(response.content)

    def test_save_own_coach_profile_fails(self):
        """Test that users cannot save their own coach profile."""
        self.client.force_login(self.user)

        payload = {"coach_uuid": str(self.user_coach.uuid)}

        response = self.client.post(
            self.create_saved_coach_url,
            json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "You cannot save your own coach profile" in str(response.content)

    def test_unauthenticated_request_fails(self):
        """Test that unauthenticated requests fail."""
        payload = {"coach_uuid": str(self.approved_coach.uuid)}

        response = self.client.post(
            self.create_saved_coach_url,
            json.dumps(payload),
            content_type="application/json",
        )

        # DRF may return 403 instead of 401 depending on configuration
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]
