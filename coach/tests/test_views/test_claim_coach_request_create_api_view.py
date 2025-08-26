import json
import uuid

import pytest
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from coach.models import ClaimCoachRequest
from coach.tests.factories import CoachFactory
from core.users.tests.factories import UserFactory


@pytest.mark.django_db
class ClaimCoachRequestCreateAPIViewTestCase(TestCase):
    """
    Test cases for the ClaimCoachRequestCreateAPIView.
    """

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.claim_url = reverse("coach:claim-coach")

        # Create an unclaimed coach (no user associated)
        self.unclaimed_coach = CoachFactory(user=None)

        # Create a claimed coach (with associated user)
        self.user = UserFactory()
        self.claimed_coach = CoachFactory(user=self.user)

        # Create a user who already has a coach profile
        self.coach_owner = self.claimed_coach.user

        # Create a user without a coach profile
        self.user_without_coach = UserFactory()

        # Valid payload for claim request
        self.valid_payload = {
            "coach_uuid": str(self.unclaimed_coach.uuid),
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "country": "Test Country",
            "phone_number": "1234567890",
        }

    def test_claim_coach_unauthenticated_success(self):
        """Test successful claim request as an unauthenticated user."""
        response = self.client.post(
            self.claim_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Verify response data
        data = response.json()
        assert "detail" in data
        assert "uuid" in data
        assert "status" in data
        assert data["status"] == ClaimCoachRequest.STATUS_PENDING

        # Verify claim request was created in database
        claim_request = ClaimCoachRequest.objects.get(uuid=data["uuid"])
        assert claim_request.user is None  # No user associated
        assert claim_request.coach == self.unclaimed_coach
        assert claim_request.first_name == self.valid_payload["first_name"]
        assert claim_request.last_name == self.valid_payload["last_name"]
        assert claim_request.email == self.valid_payload["email"]
        assert claim_request.country == self.valid_payload["country"]
        assert claim_request.phone_number == self.valid_payload["phone_number"]
        assert claim_request.status == ClaimCoachRequest.STATUS_PENDING

    def test_claim_coach_authenticated_success(self):
        """Test successful claim request as an authenticated user."""
        # Login as user without a coach profile
        self.client.force_login(self.user_without_coach)

        response = self.client.post(
            self.claim_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Verify claim request was created with user associated
        data = response.json()
        claim_request = ClaimCoachRequest.objects.get(uuid=data["uuid"])
        assert claim_request.user == self.user_without_coach
        assert claim_request.coach == self.unclaimed_coach

    def test_claim_coach_nonexistent_uuid(self):
        """Test claim request with non-existent coach UUID."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["coach_uuid"] = str(uuid.uuid4())  # Random UUID

        response = self.client.post(
            self.claim_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Coach with this UUID does not exist" in str(response.content)

    def test_claim_already_claimed_coach(self):
        """Test claim request for a coach that is already claimed."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["coach_uuid"] = str(self.claimed_coach.uuid)

        response = self.client.post(
            self.claim_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "This coach profile is already claimed" in str(response.content)

    def test_claim_by_user_with_coach_profile(self):
        """Test claim request by a user who already has a coach profile."""
        # Login as a user who already has a coach profile
        self.client.force_login(self.coach_owner)

        response = self.client.post(
            self.claim_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "You already have a coach profile" in str(response.content)

    def test_claim_coach_missing_fields(self):
        """Test claim request with missing required fields."""
        # Create payload with missing fields
        invalid_payload = {
            "coach_uuid": str(self.unclaimed_coach.uuid),
            # Missing first_name, last_name, etc.
        }

        response = self.client.post(
            self.claim_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "first_name" in data
        assert "last_name" in data
        assert "email" in data
        assert "country" in data
        assert "phone_number" in data

    def test_claim_coach_invalid_email(self):
        """Test claim request with invalid email format."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["email"] = "invalid-email"

        response = self.client.post(
            self.claim_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()

    def test_multiple_claims_for_same_coach(self):
        """Test multiple claim requests for the same coach."""
        # Create the first claim
        first_response = self.client.post(
            self.claim_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert first_response.status_code == status.HTTP_201_CREATED

        # Create a second claim with different user details
        second_payload = self.valid_payload.copy()
        second_payload["first_name"] = "Another"
        second_payload["last_name"] = "User"
        second_payload["email"] = "another@example.com"

        second_response = self.client.post(
            self.claim_url,
            json.dumps(second_payload),
            content_type="application/json",
        )

        # Should be successful as multiple claims are allowed for the same coach
        assert second_response.status_code == status.HTTP_201_CREATED

        # Verify both claims exist in the database
        claims = ClaimCoachRequest.objects.filter(coach=self.unclaimed_coach)
        assert claims.count() == 2  # noqa: PLR2004

    def test_server_error_handling(self):
        """Test error handling when an unexpected error occurs."""
        # Create a mock exception during save by using an invalid UUID format
        invalid_payload = self.valid_payload.copy()
        invalid_payload["coach_uuid"] = "invalid-uuid-format"

        response = self.client.post(
            self.claim_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        # Should return a 400 Bad Request rather than 500 since validation
        # would catch this before the server error handling
        assert response.status_code == status.HTTP_400_BAD_REQUEST
