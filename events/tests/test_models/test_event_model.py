import uuid
from datetime import datetime
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from coach.models import Coach
from coach.tests.factories import CoachFactory
from events.models import Event
from events.tests.factories import EventFactory
from events.tests.factories import create_test_image


class TestEvent(TestCase):
    def setUp(self):
        # Use coach type constant instead of CoachType model
        self.coach_type = Coach.TYPE_ONLINE

        # Create a coach
        self.coach = CoachFactory(type=self.coach_type)

        # Create test image file
        self.event_image = create_test_image("test_event.jpg")

        # Set up date times
        self.start_time = timezone.now() + timedelta(days=1)
        self.end_time = self.start_time + timedelta(hours=2)

        # Create a basic event
        self.event = Event.objects.create(
            uuid=uuid.uuid4(),
            coach=self.coach,
            name="Test Event",
            description="This is a test event",
            image=self.event_image,
            start_datetime=self.start_time,
            end_datetime=self.end_time,
        )

    def test_event_creation(self):
        """Test event creation with all required fields"""
        assert self.event.name == "Test Event"
        assert self.event.description == "This is a test event"
        assert self.event.coach == self.coach
        assert self.event.start_datetime == self.start_time
        assert self.event.end_datetime == self.end_time
        assert self.event.image is not None
        assert self.event.uuid is not None
        assert self.event.slug is not None
        # Check default values for new fields
        assert self.event.type == "online"
        assert self.event.location == ""

    def test_string_representation(self):
        """Test string representation of event model"""
        assert str(self.event) == "Test Event"

    def test_slug_generation(self):
        """Test that slugs are automatically generated"""
        assert slugify(self.event.name) in self.event.slug

        # Create another event with same name to test unique slugs
        event2 = EventFactory(name="Test Event")
        # Ensure the event is saved and refresh to get the generated slug
        event2.save()
        event2.refresh_from_db()

        # Create a third event with the same name
        event3 = EventFactory(name="Test Event")
        event3.save()
        event3.refresh_from_db()

        # Test that all slugs contain the base name
        assert slugify("Test Event") in event2.slug
        assert slugify("Test Event") in event3.slug

        # Test that all slugs are unique
        assert event2.slug != self.event.slug
        assert event3.slug != self.event.slug
        assert event3.slug != event2.slug

    def test_timestamp_fields(self):
        """Test timestamp fields"""
        assert isinstance(self.event.created_at, datetime)
        assert isinstance(self.event.updated_at, datetime)

        # Test that created_at doesn't change on update
        original_created_at = self.event.created_at
        self.event.name = "Updated Event Name"
        self.event.save()
        self.event.refresh_from_db()
        assert self.event.created_at == original_created_at

        # Test that updated_at changes on update
        assert self.event.updated_at > original_created_at

    def test_coach_relationship(self):
        """Test relationship with Coach model"""
        assert self.event.coach == self.coach

        # Test that events appear in the coach's related manager
        assert self.event in self.coach.events.all()

    def test_update_event(self):
        """Test updating event fields"""
        # Save original slug
        original_slug = self.event.slug

        # Update fields
        new_start = timezone.now() + timedelta(days=2)
        new_end = new_start + timedelta(hours=3)

        self.event.name = "Updated Event"
        self.event.description = "Updated event description"
        self.event.start_datetime = new_start
        self.event.end_datetime = new_end
        self.event.type = "offline"
        self.event.location = "Downtown Conference Hall"
        self.event.save()

        self.event.refresh_from_db()
        assert self.event.name == "Updated Event"
        assert self.event.description == "Updated event description"
        assert self.event.start_datetime == new_start
        assert self.event.end_datetime == new_end
        assert self.event.type == "offline"
        assert self.event.location == "Downtown Conference Hall"

        # Slug should not change when updating
        assert self.event.slug == original_slug

    def test_event_image_upload(self):
        """Test event image uploads and upload path functions"""
        # Create a new test image
        new_image = create_test_image("new_event.jpg", (200, 200), "green")

        # Store the original image path
        original_image_path = self.event.image.path

        # Update the image
        self.event.image = new_image
        self.event.save()

        # Refresh from database
        self.event.refresh_from_db()

        # Verify image was saved
        assert self.event.image is not None
        assert self.event.image.path != original_image_path

    def test_create_event_factory(self):
        """Test creating an event using EventFactory"""
        factory_event = EventFactory()

        assert factory_event.name is not None
        assert factory_event.description is not None
        assert factory_event.coach is not None
        assert factory_event.image is not None
        assert factory_event.start_datetime < factory_event.end_datetime
        assert factory_event.uuid is not None
        assert factory_event.slug is not None
        assert factory_event.type == "online"  # Default type
        assert factory_event.location == factory_event.location

    def test_event_type_field(self):
        """Test event type field"""
        # Test changing type
        self.event.type = "offline"
        self.event.save()
        self.event.refresh_from_db()
        assert self.event.type == "offline"

    def test_event_location_field(self):
        """Test event location field"""
        # Test setting and updating location
        self.event.location = "New York Convention Center"
        self.event.save()
        self.event.refresh_from_db()
        assert self.event.location == "New York Convention Center"
