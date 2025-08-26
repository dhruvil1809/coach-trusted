import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase

from coach.models import ClaimCoachRequest
from coach.tests.factories import ClaimCoachRequestFactory
from coach.tests.factories import CoachFactory
from core.users.tests.factories import UserFactory


class TestClaimCoachRequest(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create a user that will be making the claim request
        self.user = UserFactory()

        # Create a coach with no associated user (unclaimed coach profile)
        self.unclaimed_coach = CoachFactory(user=None)

        # Create a coach with an associated user (claimed coach profile)
        self.claimed_coach = CoachFactory()

        # Create a pending claim request
        self.claim_request = ClaimCoachRequestFactory(
            user=self.user,
            coach=self.unclaimed_coach,
            status=ClaimCoachRequest.STATUS_PENDING,
        )

    def test_claim_request_creation(self):
        """Test that a claim request can be created with required fields."""
        assert self.claim_request.user == self.user
        assert self.claim_request.coach == self.unclaimed_coach
        assert self.claim_request.status == ClaimCoachRequest.STATUS_PENDING
        assert self.claim_request.rejection_reason == ""
        assert self.claim_request.approval_reason == ""
        assert self.claim_request.first_name is not None
        assert self.claim_request.last_name is not None
        assert self.claim_request.email is not None
        assert self.claim_request.country is not None
        assert self.claim_request.phone_number is not None

    def test_string_representation(self):
        """Test string representation of the claim request model."""
        coach_name = f"{self.unclaimed_coach.first_name} {self.unclaimed_coach.last_name}".strip()  # noqa: E501
        expected_str = f"Claim request for {coach_name} by {self.claim_request.first_name} {self.claim_request.last_name}"  # noqa: E501
        assert str(self.claim_request) == expected_str

    def test_uuid_generation(self):
        """Test UUID is automatically generated and unique."""
        assert self.claim_request.uuid is not None

        # Create another claim request and verify UUID is different
        another_request = ClaimCoachRequestFactory()
        assert self.claim_request.uuid != another_request.uuid

    def test_approve_claim_request(self):
        """Test approving a claim request."""
        # Set approval reason and update status
        self.claim_request.approval_reason = "Identity verified through documentation."
        self.claim_request.status = ClaimCoachRequest.STATUS_APPROVED
        self.claim_request.save()

        # Refresh coach from database
        self.unclaimed_coach.refresh_from_db()

        # Verify that the coach is now associated with the user
        assert self.unclaimed_coach.user == self.user
        assert self.claim_request.status == ClaimCoachRequest.STATUS_APPROVED

    def test_reject_claim_request(self):
        """Test rejecting a claim request."""
        # Set rejection reason and update status
        self.claim_request.rejection_reason = "Documentation insufficient."
        self.claim_request.status = ClaimCoachRequest.STATUS_REJECTED
        self.claim_request.save()

        # Refresh coach from database
        self.unclaimed_coach.refresh_from_db()

        # Verify that the coach remains unassociated
        assert self.unclaimed_coach.user is None
        assert self.claim_request.status == ClaimCoachRequest.STATUS_REJECTED

    def test_approve_without_reason_validation(self):
        """Test validation error when approving without a reason."""
        self.claim_request.status = ClaimCoachRequest.STATUS_APPROVED

        with pytest.raises(ValidationError) as error:
            self.claim_request.full_clean()

        assert "Approval reason is required when approving a request" in str(
            error.value,
        )

    def test_reject_without_reason_validation(self):
        """Test validation error when rejecting without a reason."""
        self.claim_request.status = ClaimCoachRequest.STATUS_REJECTED

        with pytest.raises(ValidationError) as error:
            self.claim_request.full_clean()

        assert "Rejection reason is required when rejecting a request" in str(
            error.value,
        )

    def test_claim_already_claimed_coach(self):
        """Test validation error when attempting to claim an already claimed coach."""
        # Try to create a claim request for a coach that already has a user
        claim_request = ClaimCoachRequestFactory.build(
            coach=self.claimed_coach,
            user=UserFactory(),
        )

        with pytest.raises(ValidationError) as error:
            claim_request.full_clean()

        assert "This coach profile is already claimed" in str(error.value)

    def test_user_with_existing_coach_profile(self):
        """Test validation error when a user with an existing coach profile attempts to claim another coach."""  # noqa: E501
        # Create a user who already has a coach profile
        user_with_coach = CoachFactory().user

        # Try to create a claim request for this user
        claim_request = ClaimCoachRequestFactory.build(
            coach=self.unclaimed_coach,
            user=user_with_coach,
        )

        with pytest.raises(ValidationError) as error:
            claim_request.full_clean()

        assert "This user already has a coach profile" in str(error.value)

    def test_approve_or_reject_without_user(self):
        """Test validation error when approving or rejecting a request without a user."""  # noqa: E501
        # Create a request without a user
        request_without_user = ClaimCoachRequestFactory(
            user=None,
            coach=self.unclaimed_coach,
        )

        # Try to approve without a user
        request_without_user.status = ClaimCoachRequest.STATUS_APPROVED
        request_without_user.approval_reason = "Approved"

        with pytest.raises(ValidationError) as error:
            request_without_user.full_clean()

        assert "User is required when approving or rejecting a request" in str(
            error.value,
        )

        # Try to reject without a user
        request_without_user.status = ClaimCoachRequest.STATUS_REJECTED
        request_without_user.rejection_reason = "Rejected"

        with pytest.raises(ValidationError) as error:
            request_without_user.full_clean()

        assert "User is required when approving or rejecting a request" in str(
            error.value,
        )

    def test_status_choices(self):
        """Test status choices for the claim request."""
        # For each status, create a fresh claim request to avoid validation errors
        for status, _ in ClaimCoachRequest.STATUS_CHOICES:
            # Create a new user and unclaimed coach for each status test
            test_user = UserFactory()
            test_coach = CoachFactory(user=None)
            test_request = ClaimCoachRequestFactory(
                user=test_user,
                coach=test_coach,
                status=ClaimCoachRequest.STATUS_PENDING,
            )

            # Set proper reasons based on status
            if status == ClaimCoachRequest.STATUS_APPROVED:
                test_request.approval_reason = "Approved for testing"
            elif status == ClaimCoachRequest.STATUS_REJECTED:
                test_request.rejection_reason = "Rejected for testing"

            test_request.status = status

            if status != ClaimCoachRequest.STATUS_PENDING:
                test_request.full_clean()
                test_request.save()
                test_request.refresh_from_db()
                assert test_request.status == status

    def test_update_claim_request(self):
        """Test updating claim request fields."""
        # Update fields
        new_first_name = "Updated First"
        new_last_name = "Updated Last"
        new_email = "updated@example.com"
        new_phone = "9876543210"
        new_country = "Updated Country"

        self.claim_request.first_name = new_first_name
        self.claim_request.last_name = new_last_name
        self.claim_request.email = new_email
        self.claim_request.phone_number = new_phone
        self.claim_request.country = new_country
        self.claim_request.save()

        # Refresh from database
        self.claim_request.refresh_from_db()

        # Verify fields were updated
        assert self.claim_request.first_name == new_first_name
        assert self.claim_request.last_name == new_last_name
        assert self.claim_request.email == new_email
        assert self.claim_request.phone_number == new_phone
        assert self.claim_request.country == new_country

    def test_multiple_pending_requests_for_same_coach(self):
        """Test multiple pending requests for the same coach."""
        # Create another user
        another_user = UserFactory()

        # Create another claim request for the same coach
        another_request = ClaimCoachRequestFactory(
            user=another_user,
            coach=self.unclaimed_coach,
        )

        # Verify both requests exist
        requests = ClaimCoachRequest.objects.filter(coach=self.unclaimed_coach)
        assert requests.count() == 2  # noqa: PLR2004

        # Approve one request
        self.claim_request.approval_reason = "Approved first request"
        self.claim_request.status = ClaimCoachRequest.STATUS_APPROVED
        self.claim_request.save()

        # Refresh coach and the other request
        self.unclaimed_coach.refresh_from_db()
        another_request.refresh_from_db()

        # Verify the coach is now associated with the user from the first request
        assert self.unclaimed_coach.user == self.user

        # The second request should now fail validation because the coach is claimed
        with pytest.raises(ValidationError):
            another_request.full_clean()
