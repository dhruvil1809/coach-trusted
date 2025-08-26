import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase

from coach.models import CoachReview
from coach.tests.factories import CoachFactory
from coach.tests.factories import CoachReviewFactory
from core.users.tests.factories import UserFactory


class TestCoachReview(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create a user who will leave a review
        self.user = UserFactory()

        # Create a coach to be reviewed
        self.coach = CoachFactory()

        # Create a pending review
        self.review = CoachReviewFactory(
            user=self.user,
            coach=self.coach,
            rating=4,
            comment="Great coaching session!",
            status=CoachReview.STATUS_PENDING,
        )

    def test_review_creation(self):
        """Test that a review can be created with required fields."""
        assert self.review.user == self.user
        assert self.review.coach == self.coach
        assert self.review.rating == 4  # noqa: PLR2004
        assert self.review.comment == "Great coaching session!"
        assert self.review.status == CoachReview.STATUS_PENDING
        assert self.review.rejection_reason == ""
        assert self.review.approval_reason == ""
        assert (
            self.review.first_name is not None
        )  # Using the field name as defined in the model
        assert self.review.last_name is not None
        assert self.review.email is not None
        assert self.review.date is not None
        assert self.review.proof_file is not None

    def test_string_representation(self):
        """Test string representation of the review model."""
        coach_name = f"{self.coach.first_name} {self.coach.last_name}".strip()
        expected_str = f"Review for {coach_name} by {self.review.first_name} {self.review.last_name}"  # noqa: E501
        assert str(self.review) == expected_str

    def test_uuid_generation(self):
        """Test UUID is automatically generated and unique."""
        assert self.review.uuid is not None

        # Create another review and verify UUID is different
        another_review = CoachReviewFactory()
        assert self.review.uuid != another_review.uuid

    def test_rating_validation(self):
        """Test validation of the rating field."""
        # Test minimum rating
        review_min = CoachReviewFactory(rating=1)
        review_min.full_clean()  # Should not raise exception

        # Test maximum rating
        review_max = CoachReviewFactory(rating=5)
        review_max.full_clean()  # Should not raise exception

        # Test rating below minimum
        review_invalid = CoachReviewFactory()
        review_invalid.rating = 0
        with pytest.raises(ValidationError):
            review_invalid.full_clean()

        # Test rating above maximum
        review_invalid.rating = 6
        with pytest.raises(ValidationError):
            review_invalid.full_clean()

    def test_approve_review(self):
        """Test approving a review."""
        # Set approval reason and update status
        self.review.approval_reason = "Review verified with proof document."
        self.review.status = CoachReview.STATUS_APPROVED
        self.review.save()

        # Verify the status was updated
        assert self.review.status == CoachReview.STATUS_APPROVED

    def test_reject_review(self):
        """Test rejecting a review."""
        # Set rejection reason and update status
        self.review.rejection_reason = "Insufficient proof of coaching session."
        self.review.status = CoachReview.STATUS_REJECTED
        self.review.save()

        # Verify the status was updated
        assert self.review.status == CoachReview.STATUS_REJECTED

    def test_approve_without_reason_validation(self):
        """Test validation error when approving without a reason."""
        self.review.status = CoachReview.STATUS_APPROVED

        with pytest.raises(ValidationError) as error:
            self.review.full_clean()

        assert "Approval reason is required when approving a review" in str(
            error.value,
        )

    def test_reject_without_reason_validation(self):
        """Test validation error when rejecting without a reason."""
        self.review.status = CoachReview.STATUS_REJECTED

        with pytest.raises(ValidationError) as error:
            self.review.full_clean()

        assert "Rejection reason is required when rejecting a review" in str(
            error.value,
        )

    def test_anonymous_review(self):
        """Test creating a review without associating a user."""
        anonymous_review = CoachReviewFactory(
            user=None,
            coach=self.coach,
        )
        anonymous_review.full_clean()  # Should not raise exception
        assert anonymous_review.user is None
