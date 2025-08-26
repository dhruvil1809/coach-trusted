import pytest
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from coach.models import Coach
from coach.tests.factories import CoachFactory
from coach.tests.factories import CoachReviewFactory
from events.tests.factories import EventFactory
from events.tests.factories import EventMediaFactory
from events.tests.factories import EventTicketFactory


@pytest.mark.django_db
class EventRetrieveAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Use coach type constant instead of CoachType model
        self.coach_type = Coach.TYPE_ONLINE

        # Create coach
        self.coach = CoachFactory(
            first_name="Event Test",
            last_name="Coach",
            type=self.coach_type,
            website="https://eventcoach.com",
            email="eventcoach@example.com",
            phone_number="+1234567890",
            location="New York",
            verification_status="verified",
            experience_level="expert",
        )

        # Create event
        self.event = EventFactory(
            name="Test Event",
            description="This is a test event for the retrieve API",
            coach=self.coach,
            start_datetime=timezone.now() + timezone.timedelta(days=1),
            end_datetime=timezone.now() + timezone.timedelta(days=1, hours=2),
        )

        # Create tickets for the event
        self.standard_ticket = EventTicketFactory(
            event=self.event,
            ticket_type="Standard",
            price="49.99",
        )

        self.vip_ticket = EventTicketFactory(
            event=self.event,
            ticket_type="VIP",
            price="99.99",
        )

        # URL for event detail
        self.detail_url = reverse("events:detail", kwargs={"slug": self.event.slug})

    def test_retrieve_event_success(self):
        """Test successful retrieval of an event (no authentication required)"""
        response = self.client.get(self.detail_url)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["name"] == self.event.name
        assert data["description"] == self.event.description
        assert "short_description" in data
        assert "is_featured" in data
        assert "is_saved" in data
        assert "is_saved_uuid" in data
        assert data["coach"]["id"] == self.coach.id
        assert data["coach"]["first_name"] == self.coach.first_name
        assert data["coach"]["last_name"] == self.coach.last_name
        assert "start_datetime" in data
        assert "end_datetime" in data
        assert "tickets" in data
        assert len(data["tickets"]) == 2  # We created two tickets  # noqa: PLR2004

        # Check comprehensive coach fields
        coach = data["coach"]
        assert "uuid" in coach
        assert "profile_picture" in coach
        assert "cover_image" in coach
        assert "type" in coach
        assert "website" in coach
        assert "email" in coach
        assert "phone_number" in coach
        assert "location" in coach
        assert "category" in coach
        assert "subcategory" in coach
        assert "verification_status" in coach
        assert "experience_level" in coach
        assert "is_claimable" in coach
        assert "avg_rating" in coach
        assert "review_count" in coach

        # Verify ticket data
        ticket_types = [ticket["ticket_type"] for ticket in data["tickets"]]
        assert "Standard" in ticket_types
        assert "VIP" in ticket_types

    def test_retrieve_nonexistent_event(self):
        """Test 404 response when trying to retrieve a non-existent event"""
        non_existent_url = reverse(
            "events:detail",
            kwargs={"slug": "non-existent-slug"},
        )
        response = self.client.get(non_existent_url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_event_with_media(self):
        """Test retrieving an event with associated media files"""
        # Create media files for the event (assuming EventMediaFactory exists)
        EventMediaFactory(event=self.event)
        EventMediaFactory(event=self.event)

        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "media" in data
        assert len(data["media"]) == 2  # noqa: PLR2004

        # Check that media files have expected fields
        assert "id" in data["media"][0]
        assert "file" in data["media"][0]
        assert "created_at" in data["media"][0]

    def test_event_type_in_detail(self):
        """Test that event type (online/offline) is correctly displayed in the detail view"""  # noqa: E501
        # Set the event type to online
        self.event.type = "online"
        self.event.save()

        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "type" in data
        assert data["type"] == "online"

        # Update the event type to offline
        self.event.type = "offline"
        self.event.save()

        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "type" in data
        assert data["type"] == "offline"

    def test_event_location_in_detail(self):
        """Test that event location is correctly displayed in the detail view"""
        # Set a specific location for the event
        self.event.location = "Conference Center, Room 123"
        self.event.save()

        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "location" in data
        assert data["location"] == "Conference Center, Room 123"

    def test_is_saved_and_is_saved_uuid_fields_for_unauthenticated_user(self):
        """Test that is_saved and is_saved_uuid fields work for unauthenticated users"""
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Check that event has is_saved=False and is_saved_uuid=None for
        # unauthenticated users
        assert "is_saved" in data
        assert "is_saved_uuid" in data
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None

    def test_is_saved_and_is_saved_uuid_fields_for_authenticated_user(self):
        """Test that is_saved and is_saved_uuid fields work correctly for
        authenticated users"""
        from core.users.tests.factories import UserFactory
        from events.tests.factories import SavedEventFactory

        # Create a user and authenticate
        user = UserFactory()
        self.client.force_login(user)

        # Test event not saved by user
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "is_saved" in data
        assert "is_saved_uuid" in data
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None

        # Save the event for this user
        saved_event = SavedEventFactory(user=user, event=self.event)

        # Test event saved by user
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_saved"] is True
        assert data["is_saved_uuid"] == str(saved_event.uuid)

    def test_is_saved_uuid_field_functionality_multiple_users(self):
        """Test is_saved_uuid field functionality with multiple users."""
        from core.users.tests.factories import UserFactory
        from events.tests.factories import SavedEventFactory

        # Create two different users
        user1 = UserFactory()
        user2 = UserFactory()

        # Create saved event record for user1
        saved_event1 = SavedEventFactory(user=user1, event=self.event)

        # Test with user1 authentication
        self.client.force_login(user1)
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # User1 should see their saved event with correct UUID
        assert data["is_saved"] is True
        assert data["is_saved_uuid"] == str(saved_event1.uuid)

        # Test with user2 authentication (event not saved by user2)
        self.client.force_login(user2)
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # User2 should not see event as saved
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None

        # Save event for user2
        saved_event2 = SavedEventFactory(user=user2, event=self.event)

        # Test again with user2 authentication (now event is saved)
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # User2 should see their saved event with correct UUID
        assert data["is_saved"] is True
        assert data["is_saved_uuid"] == str(saved_event2.uuid)

        # Test after logout (unauthenticated)
        self.client.logout()
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Event should show as not saved for unauthenticated users
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None

    def test_coach_avg_rating_and_review_count_in_event_detail(self):
        """Test that coach avg_rating and review_count are correctly populated"""
        from coach.models import CoachReview

        # Expected values
        expected_avg_rating = 4.0  # Average of 5, 4, and 3
        expected_review_count = 3  # Three approved reviews

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
        CoachReviewFactory(
            coach=self.coach,
            rating=3,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-03",
        )

        # Create a pending review that shouldn't affect the averages
        CoachReviewFactory(
            coach=self.coach,
            rating=1,
            status=CoachReview.STATUS_PENDING,
            date="2025-01-04",
        )

        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        coach_data = data["coach"]

        # Verify the coach has the correct avg_rating and review_count
        assert coach_data["avg_rating"] == expected_avg_rating
        assert coach_data["review_count"] == expected_review_count

    def test_coach_with_no_reviews_in_event_detail(self):
        """Test that coach with no reviews shows 0.0 avg_rating and 0 review_count"""
        # No reviews are created for this test

        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        coach_data = data["coach"]

        # Coach with no reviews should have 0.0 rating and 0 count
        assert coach_data["avg_rating"] == 0.0
        assert coach_data["review_count"] == 0

    def test_coach_rating_breakdown_in_event_detail(self):
        """Test that coach rating breakdown with individual star counts is correctly
        populated in event detail"""
        from coach.models import CoachReview

        # Expected counts for each star rating
        expected_5_star = 2
        expected_4_star = 1
        expected_3_star = 3
        expected_2_star = 1
        expected_1_star = 0
        expected_total_reviews = 7
        floating_point_tolerance = 0.01

        # Create reviews with different ratings
        # Two 5-star reviews
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

        # One 4-star review
        CoachReviewFactory(
            coach=self.coach,
            rating=4,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-03",
        )

        # Three 3-star reviews
        CoachReviewFactory(
            coach=self.coach,
            rating=3,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-04",
        )
        CoachReviewFactory(
            coach=self.coach,
            rating=3,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-05",
        )
        CoachReviewFactory(
            coach=self.coach,
            rating=3,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-06",
        )

        # One 2-star review
        CoachReviewFactory(
            coach=self.coach,
            rating=2,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-07",
        )

        # No 1-star reviews

        # Create a pending review that shouldn't affect the breakdown
        CoachReviewFactory(
            coach=self.coach,
            rating=1,
            status=CoachReview.STATUS_PENDING,
            date="2025-01-08",
        )

        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        coach_data = data["coach"]

        # Verify the coach has rating_breakdown field
        assert "rating_breakdown" in coach_data
        rating_breakdown = coach_data["rating_breakdown"]

        # Verify individual star counts
        assert rating_breakdown["5_star"] == expected_5_star
        assert rating_breakdown["4_star"] == expected_4_star
        assert rating_breakdown["3_star"] == expected_3_star
        assert rating_breakdown["2_star"] == expected_2_star
        assert rating_breakdown["1_star"] == expected_1_star

        # Verify total count matches review_count
        total_stars = sum(rating_breakdown.values())
        assert coach_data["review_count"] == total_stars
        assert coach_data["review_count"] == expected_total_reviews

        # Verify average rating calculation
        # (5*2 + 4*1 + 3*3 + 2*1 + 1*0) / 7 = (10 + 4 + 9 + 2 + 0) / 7 = 25/7 ≈ 3.57
        expected_avg = 25.0 / expected_total_reviews
        rating_diff = abs(coach_data["avg_rating"] - expected_avg)
        assert rating_diff < floating_point_tolerance

    def test_coach_rating_breakdown_with_no_reviews_in_event_detail(self):
        """Test that coach with no reviews shows all star counts as 0 in event detail"""
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        coach_data = data["coach"]

        # Verify the coach has rating_breakdown field
        assert "rating_breakdown" in coach_data
        rating_breakdown = coach_data["rating_breakdown"]

        # All star counts should be 0
        assert rating_breakdown["5_star"] == 0
        assert rating_breakdown["4_star"] == 0
        assert rating_breakdown["3_star"] == 0
        assert rating_breakdown["2_star"] == 0
        assert rating_breakdown["1_star"] == 0

        # Verify other rating fields are also 0
        assert coach_data["avg_rating"] == 0.0
        assert coach_data["review_count"] == 0

    def test_coach_rating_breakdown_only_approved_reviews_in_event_detail(self):
        """Test that only approved reviews are counted in rating breakdown
        in event detail"""
        from coach.models import CoachReview

        expected_approved_reviews = 2
        expected_avg_rating = 4.5

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

        # Create non-approved reviews (these should not be counted)
        CoachReviewFactory(
            coach=self.coach,
            rating=5,
            status=CoachReview.STATUS_PENDING,
            date="2025-01-03",
        )
        CoachReviewFactory(
            coach=self.coach,
            rating=3,
            status=CoachReview.STATUS_REJECTED,
            date="2025-01-04",
        )

        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        coach_data = data["coach"]

        # Verify rating breakdown only includes approved reviews
        rating_breakdown = coach_data["rating_breakdown"]
        assert rating_breakdown["5_star"] == 1  # Only one approved 5-star
        assert rating_breakdown["4_star"] == 1  # One approved 4-star
        # No approved 3-star (rejected one doesn't count)
        assert rating_breakdown["3_star"] == 0
        assert rating_breakdown["2_star"] == 0
        assert rating_breakdown["1_star"] == 0

        # Verify total counts
        assert coach_data["review_count"] == expected_approved_reviews
        assert coach_data["avg_rating"] == expected_avg_rating
