import json

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from coach.models import Coach
from coach.models import CoachReview
from coach.tests.factories import CoachFactory
from coach.tests.factories import CoachMediaFactory
from coach.tests.factories import CoachReviewFactory
from core.users.models import User


class CoachRetrieveUpdateAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users
        self.user1 = User.objects.create_user(
            username="coachuser",
            email="coach@example.com",
            password="StrongPassword123",  # noqa: S106
            is_active=True,
        )

        self.user2 = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="StrongPassword123",  # noqa: S106
            is_active=True,
        )

        # Create coaches
        self.coach = CoachFactory(
            user=self.user1,
            title="API Test Coach",  # Add title
            first_name="Test",
            last_name="Coach",
            website="https://testcoach.com",
            email="testcoach@example.com",
            phone_number="+1234567890",
            location="New York",
            verification_status="verified",
            experience_level="expert",
            type="life",  # Add coach type as a text choice
        )

        # URL for coach detail - use uuid instead of id
        self.detail_url = reverse(
            "coach:retrieve-update",
            kwargs={"uuid": self.coach.uuid},
        )

        # Update payload
        self.valid_payload = {
            "title": "Updated Title",  # Add title
            "first_name": "Updated",
            "last_name": "Coach Name",
            "website": "https://updatedcoach.com",
            "email": "updated@example.com",
            "phone_number": "+0987654321",
            "location": "Updated Location",
            "type": Coach.TYPE_OFFLINE,
        }

        self.invalid_payload = {
            "first_name": "",  # Empty first_name should be invalid
            "website": "invalid-website",  # Invalid URL format
        }

    def test_retrieve_coach_success(self):  # noqa: PLR0915
        """Test successful retrieval of a coach (no authentication required)"""
        # Create approved reviews
        CoachReviewFactory(
            coach=self.coach,
            rating=5,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-01",
        )
        CoachReviewFactory(
            coach=self.coach,
            rating=4,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-02",
        )
        # Create a pending review that shouldn't affect the averages
        CoachReviewFactory(
            coach=self.coach,
            rating=1,
            status=CoachReview.STATUS_PENDING,
            date="2025-01-03",
        )
        # Create media for the coach
        media1 = CoachMediaFactory(coach=self.coach)
        media2 = CoachMediaFactory(coach=self.coach)

        response = self.client.get(self.detail_url)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["title"] == self.coach.title  # Check title in response
        assert data["first_name"] == self.coach.first_name
        assert data["last_name"] == self.coach.last_name
        assert data["email"] == self.coach.email
        assert data["website"] == self.coach.website
        assert data["phone_number"] == self.coach.phone_number
        assert data["location"] == self.coach.location
        assert data["company"] == self.coach.company  # Check company field
        assert data["verification_status"] == self.coach.verification_status
        assert data["experience_level"] == self.coach.experience_level
        # New fields
        assert data["street_no"] == self.coach.street_no
        assert data["zip_code"] == self.coach.zip_code
        assert data["city"] == self.coach.city
        assert data["country"] == self.coach.country
        # Check rating and review count
        assert "avg_rating" in data
        assert "review_count" in data
        assert data["avg_rating"] == 4.5  # Average of 5 and 4  # noqa: PLR2004
        assert data["review_count"] == 2  # Two approved reviews  # noqa: PLR2004
        # Check total_events and total_products fields
        assert "total_events" in data
        assert "total_products" in data

        # Check category and subcategory fields are present
        assert "category" in data
        assert "subcategory" in data

        # Verify category structure (should have id, uuid, name)
        if data["category"]:
            assert "id" in data["category"]
            assert "uuid" in data["category"]
            assert "name" in data["category"]
            # Should not include description
            assert "description" not in data["category"]

        # Verify subcategory structure (list of objects with id, uuid, name)
        assert isinstance(data["subcategory"], list)
        for subcategory in data["subcategory"]:
            assert "id" in subcategory
            assert "uuid" in subcategory
            assert "name" in subcategory
            # Should not include description
            assert "description" not in subcategory

        # Check media field
        assert "media" in data
        assert isinstance(data["media"], list)
        assert len(data["media"]) == 2  # noqa: PLR2004
        media_ids = {m["id"] for m in data["media"]}
        assert media1.id in media_ids
        assert media2.id in media_ids
        for media in data["media"]:
            assert "id" in media
            assert "file" in media
            assert "created_at" in media

        # Check is_saved and is_claimable fields
        assert "is_saved" in data
        assert "is_saved_uuid" in data
        assert "is_claimable" in data
        # For unauthenticated user, is_saved should be False
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None
        # Since coach has a user, is_claimable should be False
        assert data["is_claimable"] is False

    def test_update_coach_success(self):
        """Test successful update of a coach by the owner"""
        # Login as the coach's user
        self.client.login(
            username="coachuser",
            password="StrongPassword123",  # noqa: S106
        )

        response = self.client.put(
            self.detail_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify coach was updated
        self.coach.refresh_from_db()
        assert self.coach.title == self.valid_payload["title"]  # Check title updated
        assert self.coach.first_name == self.valid_payload["first_name"]
        assert self.coach.last_name == self.valid_payload["last_name"]
        assert self.coach.website == self.valid_payload["website"]
        assert self.coach.email == self.valid_payload["email"]
        assert self.coach.phone_number == self.valid_payload["phone_number"]
        assert self.coach.location == self.valid_payload["location"]
        if "company" in self.valid_payload:
            assert self.coach.company == self.valid_payload["company"]
        # New fields should remain unchanged if not updated
        assert self.coach.street_no == self.coach.street_no
        assert self.coach.zip_code == self.coach.zip_code
        assert self.coach.city == self.coach.city
        assert self.coach.country == self.coach.country

    def test_update_coach_response_data(self):
        """Test response data after successful update contains all updated fields"""
        # Login as the coach's user
        self.client.login(
            username="coachuser",
            password="StrongPassword123",  # noqa: S106
        )

        response = self.client.put(
            self.detail_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify response data contains updated fields
        data = response.json()
        assert data["title"] == self.valid_payload["title"]  # Check title in response
        assert data["first_name"] == self.valid_payload["first_name"]
        assert data["last_name"] == self.valid_payload["last_name"]
        assert data["website"] == self.valid_payload["website"]
        assert data["email"] == self.valid_payload["email"]
        assert data["phone_number"] == self.valid_payload["phone_number"]
        assert data["location"] == self.valid_payload["location"]
        if "company" in self.valid_payload:
            assert data["company"] == self.valid_payload["company"]
        assert data["type"] == self.valid_payload["type"]
        # New fields should be present in response
        assert "street_no" in data
        assert "zip_code" in data
        assert "city" in data
        assert "country" in data

        # Check category and subcategory fields are present in response
        assert "category" in data
        assert "subcategory" in data

        # Verify category structure (should have id, uuid, name)
        if data["category"]:
            assert "id" in data["category"]
            assert "uuid" in data["category"]
            assert "name" in data["category"]
            # Should not include description
            assert "description" not in data["category"]

        # Verify subcategory structure (list of objects with id, uuid, name)
        assert isinstance(data["subcategory"], list)
        for subcategory in data["subcategory"]:
            assert "id" in subcategory
            assert "uuid" in subcategory
            assert "name" in subcategory
            # Should not include description
            assert "description" not in subcategory

    def test_update_coach_unauthenticated(self):
        """Test updating coach without authentication fails"""
        response = self.client.put(
            self.detail_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_coach_wrong_user(self):
        """Test updating coach by a different user fails"""
        # Login as a different user (not the coach's user)
        self.client.login(
            username="otheruser",
            password="StrongPassword123",  # noqa: S106
        )

        response = self.client.put(
            self.detail_url,
            json.dumps(self.valid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_coach_invalid_data(self):
        """Test updating coach with invalid data fails"""
        # Login as the coach's user
        self.client.login(
            username="coachuser",
            password="StrongPassword123",  # noqa: S106
        )

        response = self.client.put(
            self.detail_url,
            json.dumps(self.invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Ensure the coach data was not changed
        self.coach.refresh_from_db()
        assert self.coach.first_name != self.invalid_payload["first_name"]
        assert self.coach.website != self.invalid_payload["website"]

    def test_retrieve_nonexistent_coach(self):
        """Test 404 response when trying to retrieve a non-existent coach"""
        # Use a non-existent UUID format
        non_existent_url = reverse(
            "coach:retrieve-update",
            kwargs={"uuid": "00000000-0000-0000-0000-000000000000"},
        )
        response = self.client.get(non_existent_url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_partial_update_coach(self):
        """Test partial update (PATCH) of a coach by the owner"""
        # Login as the coach's user
        self.client.login(
            username="coachuser",
            password="StrongPassword123",  # noqa: S106
        )

        # Only update first_name, last_name and location
        partial_payload = {
            "title": "Partial Title",  # Add title
            "first_name": "Partially",
            "last_name": "Updated Coach",
            "location": "San Francisco",
        }

        response = self.client.patch(
            self.detail_url,
            json.dumps(partial_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify coach was partially updated
        self.coach.refresh_from_db()
        assert self.coach.title == partial_payload["title"]  # Check title updated
        assert self.coach.first_name == partial_payload["first_name"]
        assert self.coach.last_name == partial_payload["last_name"]
        assert self.coach.location == partial_payload["location"]
        # Other fields should remain unchanged
        assert self.coach.website == "https://testcoach.com"
        assert self.coach.email == "testcoach@example.com"
        # Company should remain unchanged if not updated
        assert self.coach.company == self.coach.company
        # New fields should remain unchanged if not updated
        assert self.coach.street_no == self.coach.street_no
        assert self.coach.zip_code == self.coach.zip_code
        assert self.coach.city == self.coach.city
        assert self.coach.country == self.coach.country

        # Verify response contains updated data
        data = response.json()
        assert data["title"] == partial_payload["title"]  # Check title in response
        assert data["first_name"] == partial_payload["first_name"]
        assert data["last_name"] == partial_payload["last_name"]
        assert data["location"] == partial_payload["location"]
        assert "company" in data
        # New fields should be present in response
        assert "street_no" in data
        assert "zip_code" in data
        assert "city" in data
        assert "country" in data

    def test_retrieve_coach_with_rating_breakdown(self):
        """Test that the coach detail response includes rating breakdown"""
        # Create reviews with different ratings
        CoachReviewFactory(
            coach=self.coach,
            rating=5,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-01",
        )
        CoachReviewFactory(
            coach=self.coach,
            rating=5,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-02",
        )
        CoachReviewFactory(
            coach=self.coach,
            rating=4,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-03",
        )
        CoachReviewFactory(
            coach=self.coach,
            rating=3,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-04",
        )
        CoachReviewFactory(
            coach=self.coach,
            rating=2,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-05",
        )
        # Create a pending review that shouldn't be counted
        CoachReviewFactory(
            coach=self.coach,
            rating=1,
            status=CoachReview.STATUS_PENDING,
            date="2025-01-06",
        )

        response = self.client.get(self.detail_url)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        # Check that rating_breakdown exists
        assert "rating_breakdown" in data

        # Verify the rating breakdown structure and counts
        rating_breakdown = data["rating_breakdown"]
        assert "5_star" in rating_breakdown
        assert "4_star" in rating_breakdown
        assert "3_star" in rating_breakdown
        assert "2_star" in rating_breakdown
        assert "1_star" in rating_breakdown

        # Verify the counts (only approved reviews should be counted)
        assert rating_breakdown["5_star"] == 2  # Two 5-star reviews  # noqa: PLR2004
        assert rating_breakdown["4_star"] == 1  # One 4-star review
        assert rating_breakdown["3_star"] == 1  # One 3-star review
        assert rating_breakdown["2_star"] == 1  # One 2-star review
        assert rating_breakdown["1_star"] == 0  # No approved 1-star reviews

        # Verify total count matches review_count
        total_breakdown = sum(rating_breakdown.values())
        assert data["review_count"] == total_breakdown
        assert data["review_count"] == 5  # Five approved reviews  # noqa: PLR2004

    def test_update_coach_about_field(self):
        """Test updating the about field via the coach detail API endpoint."""
        self.client.login(
            username="coachuser",
            password="StrongPassword123",  # noqa: S106
        )
        payload = {"about": "Updated about section from API."}
        response = self.client.patch(
            self.detail_url,
            json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK
        self.coach.refresh_from_db()
        assert self.coach.about == payload["about"]
        data = response.json()
        assert data["about"] == payload["about"]

        # Test clearing the about field
        payload = {"about": ""}
        response = self.client.patch(
            self.detail_url,
            json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK
        self.coach.refresh_from_db()
        assert self.coach.about == ""
        data = response.json()
        assert data["about"] == ""

    def test_is_saved_field_for_authenticated_user(self):
        """Test that is_saved field correctly indicates if coach is saved by user"""
        from coach.tests.factories import SavedCoachFactory
        from core.users.tests.factories import UserFactory

        # Create a user different from the coach's user
        user = UserFactory()

        # Test without saving the coach first
        self.client.force_login(user)
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "is_saved" in data
        assert "is_saved_uuid" in data
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None

        # Now save the coach for this user
        saved_coach = SavedCoachFactory(user=user, coach=self.coach)

        # Make request again
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "is_saved" in data
        assert "is_saved_uuid" in data
        assert data["is_saved"] is True
        assert data["is_saved_uuid"] == str(saved_coach.uuid)

    def test_is_saved_field_for_unauthenticated_user(self):
        """Test that is_saved field is False for unauthenticated users"""
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "is_saved" in data
        assert "is_saved_uuid" in data
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None

    def test_is_claimable_field_in_response(self):
        """Test that is_claimable field is present and correct in response"""
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "is_claimable" in data
        # Since the test coach has a user, it should not be claimable
        assert data["is_claimable"] is False

        # Test with a coach that has no user (claimable)
        from coach.tests.factories import CoachFactory

        claimable_coach = CoachFactory(user=None)
        claimable_url = reverse(
            "coach:retrieve-update",
            kwargs={"uuid": claimable_coach.uuid},
        )

        response = self.client.get(claimable_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "is_claimable" in data
        assert data["is_claimable"] is True

    def test_is_saved_uuid_field_functionality(self):
        """Test comprehensive functionality of is_saved_uuid field in detail view"""
        from coach.tests.factories import SavedCoachFactory
        from core.users.tests.factories import UserFactory

        # Create two different users
        user1 = UserFactory()
        user2 = UserFactory()

        # Test with user1 - coach not saved
        self.client.force_login(user1)
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None

        # Save the coach for user1
        saved_coach = SavedCoachFactory(user=user1, coach=self.coach)

        # Test again - should now show as saved with UUID
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_saved"] is True
        assert data["is_saved_uuid"] == str(saved_coach.uuid)

        # Test with user2 - should not see coach as saved (different user)
        self.client.force_login(user2)
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None

        # Save the coach for user2 as well
        saved_coach2 = SavedCoachFactory(user=user2, coach=self.coach)

        # Test again - user2 should see their own saved UUID
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_saved"] is True
        assert data["is_saved_uuid"] == str(saved_coach2.uuid)
        # Should be different from user1's UUID
        assert data["is_saved_uuid"] != str(saved_coach.uuid)

        # Test unauthenticated access
        self.client.logout()
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None
