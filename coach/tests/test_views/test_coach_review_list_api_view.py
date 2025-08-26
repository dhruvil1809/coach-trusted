import uuid

import pytest
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from coach.models import Coach
from coach.models import CoachReview
from coach.tests.factories import CoachFactory
from coach.tests.factories import CoachReviewFactory
from core.users.tests.factories import UserFactory


@pytest.mark.django_db
class CoachReviewListAPIViewTestCase(TestCase):
    """
    Test cases for the CoachReviewListAPIView.
    """

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create a coach
        self.coach = CoachFactory()

        # Create a second coach for testing filtering
        self.other_coach = CoachFactory()

        # Create a user
        self.user = UserFactory()

        # Create various review types for the first coach
        # Approved reviews
        self.approved_reviews = []
        for i in range(3):
            review = CoachReviewFactory(
                coach=self.coach,
                status=CoachReview.STATUS_APPROVED,
                approval_reason="Test approval reason",
                rating=5 - i,  # Different ratings for sorting tests
            )
            self.approved_reviews.append(review)

        # Pending reviews
        self.pending_reviews = []
        for i in range(2):  # noqa: B007
            review = CoachReviewFactory(
                coach=self.coach,
                status=CoachReview.STATUS_PENDING,
            )
            self.pending_reviews.append(review)

        # Rejected reviews
        self.rejected_reviews = []
        for i in range(1):  # noqa: B007
            review = CoachReviewFactory(
                coach=self.coach,
                status=CoachReview.STATUS_REJECTED,
                rejection_reason="Test rejection reason",
            )
            self.rejected_reviews.append(review)

        # Create some reviews for the other coach
        self.other_coach_reviews = []
        for i in range(2):  # noqa: B007
            review = CoachReviewFactory(
                coach=self.other_coach,
                status=CoachReview.STATUS_APPROVED,
                approval_reason="Test approval reason",
            )
            self.other_coach_reviews.append(review)

        # URL for accessing the coach's reviews
        self.reviews_url = reverse(
            "coach:list-reviews",
            kwargs={"coach_uuid": self.coach.uuid},
        )

    def test_get_approved_reviews_success(self):
        """Test getting approved reviews for a coach."""
        response = self.client.get(self.reviews_url)

        assert response.status_code == status.HTTP_200_OK

        # Parse response data
        data = response.json()

        # Verify pagination structure
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data

        # Verify we got only the approved reviews for the requested coach
        assert data["count"] == len(self.approved_reviews)

        # Ensure approved reviews UUIDs are in the response
        review_uuids = [review["uuid"] for review in data["results"]]
        for review in self.approved_reviews:
            assert str(review.uuid) in review_uuids

        # Ensure no pending or rejected reviews are returned
        for review in self.pending_reviews + self.rejected_reviews:
            assert str(review.uuid) not in review_uuids

    def test_invalid_uuid_format(self):
        """Test providing an invalid UUID format."""
        url = reverse("coach:list-reviews", kwargs={"coach_uuid": "not-a-uuid"})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid coach UUID format" in str(response.content)

    def test_nonexistent_coach(self):
        """Test retrieving reviews for a non-existent coach."""
        random_uuid = uuid.uuid4()
        url = reverse("coach:list-reviews", kwargs={"coach_uuid": random_uuid})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Coach not found" in str(response.content)

    def test_unapproved_coach(self):
        """Test retrieving reviews for an unapproved coach."""
        # Create an unapproved coach with reviews
        unapproved_coach = CoachFactory(review_status=Coach.REVIEW_PENDING)
        CoachReviewFactory(
            coach=unapproved_coach,
            status=CoachReview.STATUS_APPROVED,
            approval_reason="Test approval reason",
        )

        url = reverse(
            "coach:list-reviews",
            kwargs={"coach_uuid": unapproved_coach.uuid},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Coach not found" in str(response.content)

    def test_ordering_reviews(self):
        """Test ordering reviews by various fields."""
        # Test ordering by rating (ascending)
        response = self.client.get(f"{self.reviews_url}?ordering=rating")
        data = response.json()

        # Check if ratings are in ascending order
        ratings = [review["rating"] for review in data["results"]]
        assert ratings == sorted(ratings)

        # Test ordering by rating (descending)
        response = self.client.get(f"{self.reviews_url}?ordering=-rating")
        data = response.json()

        # Check if ratings are in descending order
        ratings = [review["rating"] for review in data["results"]]
        assert ratings == sorted(ratings, reverse=True)

        # Test ordering by creation date
        response = self.client.get(f"{self.reviews_url}?ordering=created_at")
        data = response.json()

        # Ensure the response is successful
        assert response.status_code == status.HTTP_200_OK

    def test_pagination(self):
        """Test pagination of reviews."""
        # Create more reviews to test pagination
        for _i in range(12):  # Adding 12 more approved reviews
            CoachReviewFactory(
                coach=self.coach,
                status=CoachReview.STATUS_APPROVED,
                approval_reason="Pagination test",
            )

        # Get the first page with 5 items
        response = self.client.get(f"{self.reviews_url}?page=1&page_size=5")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert len(data["results"]) == 5  # noqa: PLR2004
        assert data["next"] is not None  # Should have next page
        assert data["previous"] is None  # First page has no previous

        # Get the second page
        response = self.client.get(f"{self.reviews_url}?page=2&page_size=5")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert len(data["results"]) == 5  # noqa: PLR2004
        assert data["next"] is not None  # Should have next page
        assert data["previous"] is not None  # Should have previous page

        # Test with invalid page number
        response = self.client.get(f"{self.reviews_url}?page=999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
