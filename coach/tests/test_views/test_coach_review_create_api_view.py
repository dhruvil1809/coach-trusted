import json
import uuid
from datetime import date
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from coach.models import Coach
from coach.models import CoachReview
from coach.tests.factories import CoachFactory
from core.users.tests.factories import UserFactory


@pytest.mark.django_db
class CoachReviewCreateAPIViewTestCase(TestCase):
    """
    Test cases for the CoachReviewCreateAPIView.
    """

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.reviews_url = reverse("coach:create-review")

        # Create a coach
        self.coach = CoachFactory()

        # Create a user who will submit a review
        self.user = UserFactory()

        # Create a proof file for testing
        proof_file = BytesIO(b"Test file content")
        proof_file.name = "test_proof.pdf"
        self.proof_file = SimpleUploadedFile(
            "test_proof.pdf",
            proof_file.read(),
            content_type="application/pdf",
        )

        # Valid payload for review
        today = date.today().isoformat()  # noqa: DTZ011
        self.valid_payload = {
            "coach_uuid": str(self.coach.uuid),
            "rating": 4,
            "comment": "Great coaching session!",
            "date": today,
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
        }

    def test_create_review_unauthenticated_success(self):
        """Test successful review creation as an unauthenticated user."""
        response = self.client.post(
            self.reviews_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Verify response data
        data = response.json()
        assert "detail" in data
        assert "uuid" in data
        assert "status" in data
        assert data["status"] == CoachReview.STATUS_PENDING

        # Verify review was created in database
        review = CoachReview.objects.get(uuid=data["uuid"])
        assert review.user is None  # No user associated
        assert review.coach == self.coach
        assert review.rating == self.valid_payload["rating"]
        assert review.comment == self.valid_payload["comment"]
        assert review.date.isoformat() == self.valid_payload["date"]
        assert review.first_name == self.valid_payload["first_name"]
        assert review.last_name == self.valid_payload["last_name"]
        assert review.email == self.valid_payload["email"]
        assert review.status == CoachReview.STATUS_PENDING

    def test_create_review_authenticated_success(self):
        """Test successful review creation as an authenticated user."""
        # Login as user
        self.client.force_login(self.user)

        response = self.client.post(
            self.reviews_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Verify review was created with user associated
        data = response.json()
        review = CoachReview.objects.get(uuid=data["uuid"])
        assert review.user == self.user
        assert review.coach == self.coach

    def test_create_review_with_proof_file(self):
        """Test review creation with a proof file."""
        # Use multipart form data to include a file
        data = self.valid_payload.copy()

        response = self.client.post(
            self.reviews_url,
            {**data, "proof_file": self.proof_file},
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Verify the proof file was saved
        data = response.json()
        review = CoachReview.objects.get(uuid=data["uuid"])
        assert review.proof_file

    def test_create_review_nonexistent_coach(self):
        """Test review creation with non-existent coach UUID."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["coach_uuid"] = str(uuid.uuid4())  # Random UUID

        response = self.client.post(
            self.reviews_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_message = (
            "Coach with this UUID does not exist or is not available for reviews"
        )
        assert error_message in str(response.content)

    def test_create_review_unapproved_coach(self):
        """Test review creation with unapproved coach."""
        # Create a coach with pending review status
        unapproved_coach = CoachFactory(review_status=Coach.REVIEW_PENDING)

        invalid_payload = self.valid_payload.copy()
        invalid_payload["coach_uuid"] = str(unapproved_coach.uuid)

        response = self.client.post(
            self.reviews_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_message = (
            "Coach with this UUID does not exist or is not available for reviews"
        )
        assert error_message in str(response.content)

    def test_create_review_missing_required_fields(self):
        """Test review creation with missing required fields."""
        # Create payload with missing fields
        invalid_payload = {
            "coach_uuid": str(self.coach.uuid),
            # Missing rating, name, etc.
        }

        response = self.client.post(
            self.reviews_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "rating" in data
        assert "date" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "email" in data

    def test_create_review_invalid_rating(self):
        """Test review creation with invalid rating (out of range 1-5)."""
        # Test with rating too high
        high_payload = self.valid_payload.copy()
        high_payload["rating"] = 6

        response = self.client.post(
            self.reviews_url,
            json.dumps(high_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "rating" in response.json()

        # Test with rating too low
        low_payload = self.valid_payload.copy()
        low_payload["rating"] = 0

        response = self.client.post(
            self.reviews_url,
            json.dumps(low_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "rating" in response.json()

    def test_create_review_invalid_email(self):
        """Test review creation with invalid email format."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["email"] = "invalid-email"

        response = self.client.post(
            self.reviews_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()

    def test_multiple_reviews_for_same_coach(self):
        """Test creating multiple reviews for the same coach."""
        # Create the first review
        first_response = self.client.post(
            self.reviews_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert first_response.status_code == status.HTTP_201_CREATED

        # Create a second review
        second_payload = self.valid_payload.copy()
        second_payload["first_name"] = "Another"
        second_payload["last_name"] = "User"
        second_payload["email"] = "another@example.com"
        second_payload["rating"] = 5
        second_payload["comment"] = "Another great experience!"

        second_response = self.client.post(
            self.reviews_url,
            json.dumps(second_payload),
            content_type="application/json",
        )

        assert second_response.status_code == status.HTTP_201_CREATED

        # Verify both reviews exist in the database
        reviews = CoachReview.objects.filter(coach=self.coach)
        assert reviews.count() == 2  # noqa: PLR2004
