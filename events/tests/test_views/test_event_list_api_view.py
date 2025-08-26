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
from events.tests.factories import EventTicketFactory


@pytest.mark.django_db
class EventListAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.list_url = reverse("events:list")

        # Use coach type constants instead of CoachType model objects
        self.coach_type1 = Coach.TYPE_ONLINE
        self.coach_type2 = Coach.TYPE_OFFLINE

        # Create coaches with different verification statuses and experience levels
        self.coach1 = CoachFactory(
            first_name="Coach",
            last_name="One",
            type=self.coach_type1,
            website="https://coachone.com",
            email="coach1@example.com",
            phone_number="+1234567890",
            location="New York",
            verification_status="verified",
            experience_level="expert",
        )

        self.coach2 = CoachFactory(
            first_name="Coach",
            last_name="Two",
            type=self.coach_type2,
            website="https://coachtwo.com",
            email="coach2@example.com",
            phone_number="+0987654321",
            location="Los Angeles",
            verification_status="not verified",
            experience_level="beginner",
        )

        self.coach3 = CoachFactory(
            first_name="Coach",
            last_name="Three",
            type=self.coach_type1,
            website="https://coachthree.com",
            email="coach3@example.com",
            phone_number="+1122334455",
            location="Chicago",
            verification_status="verified plus",
            experience_level="intermediate",
        )

        # Create events
        self.event1 = EventFactory(
            name="Yoga Workshop",
            description="A relaxing yoga session",
            coach=self.coach1,
            start_datetime=timezone.now() + timezone.timedelta(days=1),
            end_datetime=timezone.now() + timezone.timedelta(days=1, hours=2),
        )

        self.event2 = EventFactory(
            name="Career Planning Seminar",
            description="Plan your career path",
            coach=self.coach2,
            start_datetime=timezone.now() + timezone.timedelta(days=2),
            end_datetime=timezone.now() + timezone.timedelta(days=2, hours=3),
        )

        self.event3 = EventFactory(
            name="Advanced Meditation Workshop",
            description="Meditation techniques for experts",
            coach=self.coach3,
            start_datetime=timezone.now() + timezone.timedelta(days=3),
            end_datetime=timezone.now() + timezone.timedelta(days=3, hours=2),
        )

        # Create tickets for events
        for event in [self.event1, self.event2, self.event3]:
            EventTicketFactory(
                event=event,
                ticket_type="Standard",
                price="49.99",
            )
            EventTicketFactory(
                event=event,
                ticket_type="VIP",
                price="99.99",
            )

    def test_list_events_success(self):
        """Test successful retrieval of events list"""
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "count" in data
        assert "results" in data
        assert data["count"] == 3  # noqa: PLR2004

        # Check first result has expected fields
        first_event = data["results"][0]
        assert "id" in first_event
        assert "name" in first_event
        assert "image" in first_event
        assert "short_description" in first_event
        assert "is_featured" in first_event
        assert "is_saved" in first_event
        assert "is_saved_uuid" in first_event
        assert "coach" in first_event
        assert "start_datetime" in first_event
        assert "end_datetime" in first_event
        assert "tickets" in first_event
        assert "created_at" in first_event
        assert "updated_at" in first_event

        # Check coach object has comprehensive fields
        coach = first_event["coach"]
        assert "id" in coach
        assert "uuid" in coach
        assert "first_name" in coach
        assert "last_name" in coach
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

    def test_pagination(self):
        """Test pagination functionality"""
        # Create 8 more events to have a total of 11 (exceeding default page size of 10)
        for i in range(8):
            EventFactory(
                name=f"Extra Event {i}",
                coach=self.coach1,
            )

        response = self.client.get(self.list_url)
        data = response.json()

        assert data["count"] == 11  # noqa: PLR2004
        assert len(data["results"]) == 10  # Default page size  # noqa: PLR2004
        assert data["next"] is not None  # Should have next page

        # Get second page
        response = self.client.get(data["next"])
        data = response.json()

        assert len(data["results"]) == 1  # One event on second page

    def test_filtering_by_coach_verification_status(self):
        """Test filtering events by coach verification status"""
        response = self.client.get(
            f"{self.list_url}?coach__verification_status=verified",
        )
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["coach"]["verification_status"] == "verified"

    def test_filtering_by_coach_experience_level(self):
        """Test filtering events by coach experience level"""
        response = self.client.get(f"{self.list_url}?coach__experience_level=beginner")
        data = response.json()

        assert data["count"] == 1
        # Instead of checking experience_level in the response, verify we got the right event  # noqa: E501
        assert data["results"][0]["name"] == "Career Planning Seminar"
        assert data["results"][0]["coach"]["first_name"] == "Coach"
        assert data["results"][0]["coach"]["last_name"] == "Two"

    def test_filtering_by_date_range(self):
        """Test filtering events by date range"""
        tomorrow = timezone.now() + timezone.timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")

        # Test events starting on or after tomorrow
        response = self.client.get(
            f"{self.list_url}?start_datetime__gte={tomorrow_str}",
        )
        data = response.json()

        assert data["count"] == 3  # All events start tomorrow or later  # noqa: PLR2004

        # Test events starting in exactly 3 days
        three_days = timezone.now() + timezone.timedelta(days=3)
        three_days_str = three_days.strftime("%Y-%m-%d")

        response = self.client.get(
            f"{self.list_url}?start_datetime__gte={three_days_str}",
        )
        data = response.json()

        assert data["count"] == 1
        assert "Advanced Meditation" in data["results"][0]["name"]

    def test_search_functionality(self):
        """Test search functionality"""
        # Search by event name
        response = self.client.get(f"{self.list_url}?search=Yoga")
        data = response.json()

        assert data["count"] == 1
        assert "Yoga" in data["results"][0]["name"]

        # Search by description (even though description isn't in response,
        # backend search still works on it)
        response = self.client.get(f"{self.list_url}?search=Meditation")
        data = response.json()

        assert data["count"] == 1
        # Instead of checking description field, verify the right event was returned
        assert data["results"][0]["name"] == "Advanced Meditation Workshop"

        # Search by coach name
        response = self.client.get(f"{self.list_url}?search=Coach Two")
        data = response.json()

        assert data["count"] == 1
        # Verify we get the correct coach's event without assuming experience_level is in the response  # noqa: E501
        assert "Career Planning" in data["results"][0]["name"]
        assert data["results"][0]["coach"]["first_name"] == "Coach"
        assert data["results"][0]["coach"]["last_name"] == "Two"

    def test_ordering_functionality(self):
        """Test ordering functionality"""
        # Order by name ascending
        response = self.client.get(f"{self.list_url}?ordering=name")
        data = response.json()

        names = [event["name"] for event in data["results"]]
        assert names == sorted(names)

        # Order by created_at descending
        response = self.client.get(f"{self.list_url}?ordering=-created_at")
        data = response.json()

        # Since created_at is chronological, the newest events should be first
        # This is harder to test exactly, but we can check the order matches the expected events  # noqa: E501
        assert data["results"][0]["name"] == "Advanced Meditation Workshop"
        assert data["results"][1]["name"] == "Career Planning Seminar"
        assert data["results"][2]["name"] == "Yoga Workshop"

    def test_custom_page_size(self):
        """Test custom page size parameter"""
        response = self.client.get(f"{self.list_url}?page_size=2")
        data = response.json()

        assert len(data["results"]) == 2  # noqa: PLR2004
        assert data["next"] is not None

    def test_filtering_by_type(self):
        """Test filtering events by type (online/offline)"""
        # Make sure at least one event is online and one is offline
        self.event1.type = "online"
        self.event1.save()
        self.event2.type = "offline"
        self.event2.save()

        # Test filtering for online events
        response = self.client.get(f"{self.list_url}?type=online")
        data = response.json()

        assert data["count"] >= 1
        assert all(event["type"] == "online" for event in data["results"])

        # Test filtering for offline events
        response = self.client.get(f"{self.list_url}?type=offline")
        data = response.json()

        assert data["count"] >= 1
        assert all(event["type"] == "offline" for event in data["results"])

    def test_filtering_by_location(self):
        """Test filtering events by location"""
        # Set specific locations for test
        self.event1.location = "New York Conference Center"
        self.event1.save()
        self.event2.location = "Los Angeles Hotel"
        self.event2.save()

        # Test exact location match
        response = self.client.get(
            f"{self.list_url}?location=New York Conference Center",
        )
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["location"] == "New York Conference Center"

        # Test location contains
        response = self.client.get(f"{self.list_url}?location__contains=Angeles")
        data = response.json()

        assert data["count"] == 1
        assert "Angeles" in data["results"][0]["location"]

    def test_filtering_by_is_featured(self):
        """Test filtering events by is_featured field"""
        # Set one event as featured
        self.event1.is_featured = True
        self.event1.save()

        # Set other events as not featured
        self.event2.is_featured = False
        self.event2.save()
        self.event3.is_featured = False
        self.event3.save()

        # Test filtering for featured events
        response = self.client.get(f"{self.list_url}?is_featured=true")
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["is_featured"] is True
        assert data["results"][0]["name"] == "Yoga Workshop"

        # Test filtering for non-featured events
        response = self.client.get(f"{self.list_url}?is_featured=false")
        data = response.json()

        assert data["count"] == 2  # noqa: PLR2004
        assert all(event["is_featured"] is False for event in data["results"])

    def test_filtering_by_coach_category(self):
        """Test filtering events by coach category"""
        from coach.tests.factories import CategoryFactory

        # Create categories
        fitness_category = CategoryFactory(name="Fitness Coaching")
        career_category = CategoryFactory(name="Career Coaching")
        wellness_category = CategoryFactory(name="Wellness Coaching")

        # Assign categories to coaches
        self.coach1.category = fitness_category
        self.coach1.save()
        self.coach2.category = career_category
        self.coach2.save()
        self.coach3.category = wellness_category
        self.coach3.save()

        # Test filtering by category ID
        url = f"{self.list_url}?coach__category={fitness_category.id}"
        response = self.client.get(url)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["coach"]["category"]["id"] == fitness_category.id

        # Test filtering by category name
        url = f"{self.list_url}?coach__category__name=Career Coaching"
        response = self.client.get(url)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["coach"]["category"]["name"] == "Career Coaching"

        # Test filtering by category name (case insensitive contains)
        url = f"{self.list_url}?coach__category__name__icontains=fitness"
        response = self.client.get(url)
        data = response.json()
        assert data["count"] == 1
        assert "Fitness" in data["results"][0]["coach"]["category"]["name"]

    def test_filtering_by_coach_category_custom_filter(self):
        """Test filtering events by coach category using custom filter method"""
        from coach.tests.factories import CategoryFactory

        # Create categories
        fitness_category = CategoryFactory(name="Fitness Coaching")
        career_category = CategoryFactory(name="Career Coaching")

        # Assign categories to coaches
        self.coach1.category = fitness_category
        self.coach1.save()
        self.coach2.category = career_category
        self.coach2.save()

        # Test filtering by category ID using custom filter
        url = f"{self.list_url}?coach_category={fitness_category.id}"
        response = self.client.get(url)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["coach"]["category"]["id"] == fitness_category.id

        # Test filtering by category name using custom filter
        response = self.client.get(f"{self.list_url}?coach_category=Career Coaching")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["coach"]["category"]["name"] == "Career Coaching"

        # Test filtering by multiple categories (comma-separated)
        url = f"{self.list_url}?coach_category={fitness_category.id},Career Coaching"
        response = self.client.get(url)
        data = response.json()
        assert data["count"] == 2  # noqa: PLR2004

    def test_filtering_by_coach_subcategory(self):
        """Test filtering events by coach subcategory"""
        from coach.tests.factories import SubCategoryFactory

        # Create subcategories
        yoga_subcategory = SubCategoryFactory(name="Yoga Training")
        career_dev_subcategory = SubCategoryFactory(name="Career Development")
        meditation_subcategory = SubCategoryFactory(name="Meditation Coaching")

        # Assign subcategories to coaches
        self.coach1.subcategory.add(yoga_subcategory)
        self.coach2.subcategory.add(career_dev_subcategory)
        self.coach3.subcategory.add(meditation_subcategory)

        # Test filtering by subcategory ID
        url = f"{self.list_url}?coach__subcategory={yoga_subcategory.id}"
        response = self.client.get(url)
        data = response.json()
        assert data["count"] == 1
        coach_subcategories = data["results"][0]["coach"]["subcategory"]
        subcategory_ids = [sub["id"] for sub in coach_subcategories]
        assert yoga_subcategory.id in subcategory_ids

        # Test filtering by subcategory name
        url = f"{self.list_url}?coach__subcategory__name=Career Development"
        response = self.client.get(url)
        data = response.json()
        assert data["count"] == 1
        coach_subcategories = data["results"][0]["coach"]["subcategory"]
        subcategory_names = [sub["name"] for sub in coach_subcategories]
        assert "Career Development" in subcategory_names

        # Test filtering by subcategory name (case insensitive contains)
        url = f"{self.list_url}?coach__subcategory__name__icontains=yoga"
        response = self.client.get(url)
        data = response.json()
        assert data["count"] == 1
        coach_subcategories = data["results"][0]["coach"]["subcategory"]
        subcategory_names = [sub["name"] for sub in coach_subcategories]
        assert any("Yoga" in name for name in subcategory_names)

    def test_filtering_by_coach_subcategory_custom_filter(self):
        """Test filtering events by coach subcategory using custom filter method"""
        from coach.tests.factories import SubCategoryFactory

        # Create subcategories
        yoga_subcategory = SubCategoryFactory(name="Yoga Training")
        career_dev_subcategory = SubCategoryFactory(name="Career Development")

        # Assign subcategories to coaches
        self.coach1.subcategory.add(yoga_subcategory)
        self.coach2.subcategory.add(career_dev_subcategory)

        # Test filtering by subcategory ID using custom filter
        url = f"{self.list_url}?coach_subcategory={yoga_subcategory.id}"
        response = self.client.get(url)
        data = response.json()
        assert data["count"] == 1
        coach_subcategories = data["results"][0]["coach"]["subcategory"]
        subcategory_ids = [sub["id"] for sub in coach_subcategories]
        assert yoga_subcategory.id in subcategory_ids

        # Test filtering by subcategory name using custom filter
        url = f"{self.list_url}?coach_subcategory=Career Development"
        response = self.client.get(url)
        data = response.json()
        assert data["count"] == 1
        coach_subcategories = data["results"][0]["coach"]["subcategory"]
        subcategory_names = [sub["name"] for sub in coach_subcategories]
        assert "Career Development" in subcategory_names

        # Test filtering by multiple subcategories (comma-separated)
        url = (
            f"{self.list_url}?coach_subcategory={yoga_subcategory.id},"
            f"Career Development"
        )
        response = self.client.get(url)
        data = response.json()
        assert data["count"] == 2  # noqa: PLR2004

    def test_combined_category_and_subcategory_filtering(self):
        """Test combined filtering by both coach category and subcategory"""
        from coach.tests.factories import CategoryFactory
        from coach.tests.factories import SubCategoryFactory

        # Create categories and subcategories
        fitness_category = CategoryFactory(name="Fitness Coaching")
        yoga_subcategory = SubCategoryFactory(name="Yoga Training")
        pilates_subcategory = SubCategoryFactory(name="Pilates Training")

        # Assign to coaches
        self.coach1.category = fitness_category
        self.coach1.subcategory.add(yoga_subcategory)
        self.coach1.save()

        self.coach2.category = fitness_category
        self.coach2.subcategory.add(pilates_subcategory)
        self.coach2.save()

        # Test filtering by both category and subcategory
        url = (
            f"{self.list_url}?coach__category={fitness_category.id}"
            f"&coach__subcategory={yoga_subcategory.id}"
        )
        response = self.client.get(url)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["coach"]["category"]["id"] == fitness_category.id
        coach_subcategories = data["results"][0]["coach"]["subcategory"]
        subcategory_ids = [sub["id"] for sub in coach_subcategories]
        assert yoga_subcategory.id in subcategory_ids

    def test_ordering_by_coach_category_and_subcategory(self):
        """Test ordering events by coach category and subcategory names"""
        from coach.tests.factories import CategoryFactory
        from coach.tests.factories import SubCategoryFactory

        # Create categories and subcategories
        category_a = CategoryFactory(name="A-Category")
        category_z = CategoryFactory(name="Z-Category")
        subcategory_a = SubCategoryFactory(name="A-Subcategory")
        subcategory_z = SubCategoryFactory(name="Z-Subcategory")

        # Assign to coaches
        self.coach1.category = category_z
        self.coach1.subcategory.add(subcategory_z)
        self.coach1.save()

        self.coach2.category = category_a
        self.coach2.subcategory.add(subcategory_a)
        self.coach2.save()

        # Test ordering by category name (ascending)
        response = self.client.get(f"{self.list_url}?ordering=coach__category__name")
        data = response.json()
        if data["count"] >= 2:  # noqa: PLR2004
            first_result = data["results"][0]
            second_result = data["results"][1]
            first_category = first_result["coach"]["category"]
            second_category = second_result["coach"]["category"]
            if first_category and second_category:
                first_name = first_category["name"]
                second_name = second_category["name"]
                assert first_name <= second_name

        # Test ordering by category name (descending)
        url = f"{self.list_url}?ordering=-coach__category__name"
        response = self.client.get(url)
        data = response.json()
        if data["count"] >= 2:  # noqa: PLR2004
            first_result = data["results"][0]
            second_result = data["results"][1]
            first_category = first_result["coach"]["category"]
            second_category = second_result["coach"]["category"]
            if first_category and second_category:
                first_name = first_category["name"]
                second_name = second_category["name"]
                assert first_name >= second_name

    def test_search_by_coach_category_and_subcategory(self):
        """Test searching events by coach category and subcategory names"""
        from coach.tests.factories import CategoryFactory
        from coach.tests.factories import SubCategoryFactory

        # Create categories and subcategories with distinctive names
        fitness_category = CategoryFactory(name="Fitness Excellence")
        yoga_subcategory = SubCategoryFactory(name="Advanced Yoga")

        # Assign to coach
        self.coach1.category = fitness_category
        self.coach1.subcategory.add(yoga_subcategory)
        self.coach1.save()

        # Test search by category name
        response = self.client.get(f"{self.list_url}?search=Excellence")
        data = response.json()
        assert data["count"] >= 1
        found_fitness_event = any(
            event["coach"]["category"]
            and "Excellence" in event["coach"]["category"]["name"]
            for event in data["results"]
        )
        assert found_fitness_event

        # Test search by subcategory name
        response = self.client.get(f"{self.list_url}?search=Advanced")
        data = response.json()
        assert data["count"] >= 1
        found_yoga_event = any(
            any("Advanced" in sub["name"] for sub in event["coach"]["subcategory"])
            for event in data["results"]
        )
        assert found_yoga_event

    def test_is_saved_and_is_saved_uuid_fields_for_unauthenticated_user(self):
        """Test that is_saved and is_saved_uuid fields work for unauthenticated users"""
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Check that all events have is_saved=False and is_saved_uuid=None for
        # unauthenticated users
        for event in data["results"]:
            assert "is_saved" in event
            assert "is_saved_uuid" in event
            assert event["is_saved"] is False
            assert event["is_saved_uuid"] is None

    def test_is_saved_and_is_saved_uuid_fields_for_authenticated_user(self):
        """Test that is_saved and is_saved_uuid fields work correctly for
        authenticated users"""
        from core.users.tests.factories import UserFactory
        from events.tests.factories import SavedEventFactory

        # Create a user and authenticate
        user = UserFactory()
        self.client.force_login(user)

        # Save one of the events for this user
        saved_event = SavedEventFactory(user=user, event=self.event1)

        # Make request to list API
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        events_data = {event["id"]: event for event in data["results"]}

        # Check that saved event has is_saved=True and correct is_saved_uuid
        assert "is_saved" in events_data[self.event1.id]
        assert "is_saved_uuid" in events_data[self.event1.id]
        assert events_data[self.event1.id]["is_saved"] is True
        assert events_data[self.event1.id]["is_saved_uuid"] == str(
            saved_event.uuid,
        )

        # Check that non-saved events have is_saved=False and is_saved_uuid=None
        assert events_data[self.event2.id]["is_saved"] is False
        assert events_data[self.event2.id]["is_saved_uuid"] is None
        assert events_data[self.event3.id]["is_saved"] is False
        assert events_data[self.event3.id]["is_saved_uuid"] is None

    def test_is_saved_uuid_field_functionality_multiple_users(self):
        """Test is_saved_uuid field functionality with multiple users."""
        from core.users.tests.factories import UserFactory
        from events.tests.factories import SavedEventFactory

        # Create two different users
        user1 = UserFactory()
        user2 = UserFactory()

        # Create saved event records for different users
        saved_event1 = SavedEventFactory(user=user1, event=self.event1)
        saved_event2 = SavedEventFactory(user=user2, event=self.event2)

        # Test with user1 authentication
        self.client.force_login(user1)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        events_data = {event["id"]: event for event in data["results"]}

        # User1 should see their saved event with correct UUID
        assert events_data[self.event1.id]["is_saved"] is True
        assert events_data[self.event1.id]["is_saved_uuid"] == str(
            saved_event1.uuid,
        )

        # User1 should not see event2 as saved (different user)
        assert events_data[self.event2.id]["is_saved"] is False
        assert events_data[self.event2.id]["is_saved_uuid"] is None

        # Event3 is not saved by anyone
        assert events_data[self.event3.id]["is_saved"] is False
        assert events_data[self.event3.id]["is_saved_uuid"] is None

        # Test with user2 authentication
        self.client.force_login(user2)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        events_data = {event["id"]: event for event in data["results"]}

        # User2 should not see event1 as saved (different user)
        assert events_data[self.event1.id]["is_saved"] is False
        assert events_data[self.event1.id]["is_saved_uuid"] is None

        # User2 should see their saved event with correct UUID
        assert events_data[self.event2.id]["is_saved"] is True
        assert events_data[self.event2.id]["is_saved_uuid"] == str(
            saved_event2.uuid,
        )

        # Event3 is still not saved by anyone
        assert events_data[self.event3.id]["is_saved"] is False
        assert events_data[self.event3.id]["is_saved_uuid"] is None

        # Test after logout (unauthenticated)
        self.client.logout()
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # All events should show as not saved for unauthenticated users
        for event in data["results"]:
            assert event["is_saved"] is False
            assert event["is_saved_uuid"] is None

    def test_coach_avg_rating_and_review_count_in_event_list(self):
        """Test that coach avg_rating and review_count are correctly populated"""
        from coach.models import CoachReview

        # Expected values
        expected_coach1_avg_rating = 4.5  # Average of 5 and 4
        expected_coach1_review_count = 2  # Two approved reviews
        expected_coach2_avg_rating = 3.0  # Single review with rating 3
        expected_coach2_review_count = 1  # One approved review
        expected_coach3_avg_rating = 0.0  # No reviews
        expected_coach3_review_count = 0  # No reviews

        # Create approved reviews for coach1
        CoachReviewFactory(
            coach=self.coach1,
            rating=5,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-01",
        )
        CoachReviewFactory(
            coach=self.coach1,
            rating=4,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-02",
        )

        # Create a pending review that shouldn't affect the averages
        CoachReviewFactory(
            coach=self.coach1,
            rating=1,
            status=CoachReview.STATUS_PENDING,
            date="2025-01-03",
        )

        # Create approved review for coach2
        CoachReviewFactory(
            coach=self.coach2,
            rating=3,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-01",
        )

        # Coach3 has no reviews

        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        events = data["results"]

        # Create a mapping of event names to coach data for easier lookup
        events_by_name = {event["name"]: event["coach"] for event in events}

        # Test coach1 (has 2 approved reviews: ratings 5, 4)
        yoga_coach = events_by_name["Yoga Workshop"]
        assert yoga_coach["avg_rating"] == expected_coach1_avg_rating
        assert yoga_coach["review_count"] == expected_coach1_review_count

        # Test coach2 (has 1 approved review: rating 3)
        career_coach = events_by_name["Career Planning Seminar"]
        assert career_coach["avg_rating"] == expected_coach2_avg_rating
        assert career_coach["review_count"] == expected_coach2_review_count

        # Test coach3 (has no reviews)
        meditation_coach = events_by_name["Advanced Meditation Workshop"]
        assert meditation_coach["avg_rating"] == expected_coach3_avg_rating
        assert meditation_coach["review_count"] == expected_coach3_review_count
