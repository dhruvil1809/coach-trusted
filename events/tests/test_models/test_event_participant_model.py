import uuid
from datetime import datetime

from django.test import TestCase

from coach.models import Coach
from coach.tests.factories import CoachFactory
from events.models import EventParticipant
from events.tests.factories import EventFactory
from events.tests.factories import EventParticipantFactory


class TestEventParticipant(TestCase):
    """Tests for the EventParticipant model."""

    def setUp(self):
        """Set up test data with one event and initial participants."""
        # Use coach type constant instead of CoachType model
        self.coach_type = Coach.TYPE_ONLINE

        # Create a coach
        self.coach = CoachFactory(type=self.coach_type)

        # Create an event
        self.event = EventFactory(coach=self.coach)

        # Create 5 initial participants for basic tests
        self.participants = []
        for i in range(5):
            participant = EventParticipant.objects.create(
                event=self.event,
                first_name=f"Test{i}",
                last_name=f"Participant{i}",
                phone=f"+123456789{i}",
                email=f"test{i}@example.com",
            )
            self.participants.append(participant)

    def test_event_participant_creation(self):
        """Test creating event participants with all required fields."""
        # Verify we have 5 participant objects
        assert EventParticipant.objects.filter(event=self.event).count() == 5  # noqa: PLR2004

        # Test attributes of the first participant
        first_participant = self.participants[0]
        assert first_participant.first_name == "Test0"
        assert first_participant.last_name == "Participant0"
        assert first_participant.phone == "+1234567890"
        assert first_participant.email == "test0@example.com"
        assert first_participant.event == self.event
        assert first_participant.uuid is not None
        assert first_participant.created_at is not None
        assert first_participant.updated_at is not None

    def test_string_representation(self):
        """Test string representation of event participant."""
        participant = self.participants[0]
        expected_str = f"{self.event.name} - Test0 Participant0"
        assert str(participant) == expected_str

    def test_event_relationship(self):
        """Test relationship with Event model."""
        # Check that the event has all participants
        event_participants = self.event.participants.all()
        assert event_participants.count() == 5  # noqa: PLR2004

        # Verify all participants are associated with the event
        for participant in self.participants:
            assert participant in event_participants

        # Test that deleting the event will delete the participants (cascade)
        event_id = self.event.id
        self.event.delete()
        assert EventParticipant.objects.filter(event_id=event_id).count() == 0

    def test_uuid_generation(self):
        """Test UUID generation."""
        # All UUIDs should be unique
        uuids = [participant.uuid for participant in self.participants]
        assert len(uuids) == len(set(uuids))  # No duplicates

        # Each UUID should be a valid UUID object
        for participant_uuid in uuids:
            assert isinstance(participant_uuid, uuid.UUID)

    def test_timestamp_fields(self):
        """Test timestamp fields."""
        participant = self.participants[0]
        assert isinstance(participant.created_at, datetime)
        assert isinstance(participant.updated_at, datetime)

        # Test that created_at doesn't change on update
        original_created_at = participant.created_at
        participant.first_name = "Updated"
        participant.save()
        participant.refresh_from_db()
        assert participant.created_at == original_created_at

        # Test that updated_at changes on update
        assert participant.updated_at > original_created_at

    def test_update_participant(self):
        """Test updating participant fields."""
        participant = self.participants[1]

        # Update fields
        participant.first_name = "Updated"
        participant.last_name = "Person"
        participant.phone = "+9876543210"
        participant.email = "updated@example.com"
        participant.save()

        participant.refresh_from_db()
        assert participant.first_name == "Updated"
        assert participant.last_name == "Person"
        assert participant.phone == "+9876543210"
        assert participant.email == "updated@example.com"

    def test_create_participants_factory(self):
        """Test creating participants using EventParticipantFactory."""
        # Create new event
        new_event = EventFactory()

        # Create 3 participants with factory
        factory_participants = []
        for _ in range(3):
            factory_participant = EventParticipantFactory(event=new_event)
            factory_participants.append(factory_participant)

        # Verify participants were created
        assert EventParticipant.objects.filter(event=new_event).count() == 3  # noqa: PLR2004

        # Test basic properties
        for participant in factory_participants:
            assert participant.event == new_event
            assert participant.first_name is not None
            assert participant.last_name is not None
            assert participant.phone is not None
            assert participant.email is not None
            assert participant.uuid is not None
            assert participant.created_at is not None
            assert participant.updated_at is not None

    def test_bulk_create_1000_participants(self):
        """Test bulk creation of 1000 participants for one event."""
        # Create a new event for this test
        mass_event = EventFactory(name="Mass Event")

        # Prepare 1000 participant objects
        participants_to_create = []
        for i in range(1000):
            participants_to_create.append(  # noqa: PERF401
                EventParticipant(
                    event=mass_event,
                    first_name=f"Attendee{i}",
                    last_name=f"Person{i}",
                    phone=f"+1{str(i).zfill(10)}",
                    email=f"attendee{i}@example.com",
                ),
            )

        # Bulk create all participants
        EventParticipant.objects.bulk_create(participants_to_create)

        # Verify count
        participant_count = EventParticipant.objects.filter(event=mass_event).count()
        assert participant_count == 1000  # noqa: PLR2004

        # Test some random participants
        random_participant = EventParticipant.objects.filter(
            event=mass_event,
            first_name="Attendee500",
        ).first()

        assert random_participant is not None
        assert random_participant.last_name == "Person500"
        assert random_participant.email == "attendee500@example.com"
