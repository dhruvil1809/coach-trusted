import uuid
from datetime import datetime
from decimal import Decimal

from django.test import TestCase

from coach.models import Coach
from coach.tests.factories import CoachFactory
from events.models import EventTicket
from events.tests.factories import EventFactory
from events.tests.factories import EventTicketFactory


class TestEventTicket(TestCase):
    """Tests for the EventTicket model."""

    def setUp(self):
        """Set up test data with one event and 5 different ticket types."""
        # Use coach type constant instead of CoachType model
        self.coach_type = Coach.TYPE_ONLINE

        # Create a coach
        self.coach = CoachFactory(type=self.coach_type)

        # Create an event
        self.event = EventFactory(coach=self.coach)

        # Create 5 ticket types for the event
        self.tickets = []
        self.ticket_types = [
            "General Admission",
            "VIP",
            "Early Bird",
            "Student",
            "Group",
        ]
        self.ticket_prices = [
            Decimal("99.99"),
            Decimal("199.99"),
            Decimal("79.99"),
            Decimal("49.99"),
            Decimal("299.99"),
        ]

        for i in range(5):
            ticket = EventTicket.objects.create(
                event=self.event,
                ticket_type=self.ticket_types[i],
                price=self.ticket_prices[i],
            )
            self.tickets.append(ticket)

    def test_event_ticket_creation(self):
        """Test creating event tickets with all required fields."""
        # Verify we have 5 ticket objects
        assert EventTicket.objects.filter(event=self.event).count() == 5  # noqa: PLR2004

        # Test attributes of the first ticket
        first_ticket = self.tickets[0]
        assert first_ticket.ticket_type == "General Admission"
        assert first_ticket.price == Decimal("99.99")
        assert first_ticket.event == self.event
        assert first_ticket.uuid is not None
        assert first_ticket.created_at is not None
        assert first_ticket.updated_at is not None

    def test_string_representation(self):
        """Test string representation of event ticket."""
        ticket = self.tickets[0]
        expected_str = f"{self.event.name} - General Admission"
        assert str(ticket) == expected_str

    def test_event_relationship(self):
        """Test relationship with Event model."""
        # Check that the event has all tickets
        event_tickets = self.event.tickets.all()
        assert event_tickets.count() == 5  # noqa: PLR2004

        # Verify all tickets are associated with the event
        for ticket in self.tickets:
            assert ticket in event_tickets

        # Test that deleting the event will delete the tickets (cascade)
        event_id = self.event.id
        self.event.delete()
        assert EventTicket.objects.filter(event_id=event_id).count() == 0

    def test_uuid_generation(self):
        """Test UUID generation."""
        # All UUIDs should be unique
        uuids = [ticket.uuid for ticket in self.tickets]
        assert len(uuids) == len(set(uuids))  # No duplicates

        # Each UUID should be a valid UUID object
        for ticket_uuid in uuids:
            assert isinstance(ticket_uuid, uuid.UUID)

    def test_timestamp_fields(self):
        """Test timestamp fields."""
        ticket = self.tickets[0]
        assert isinstance(ticket.created_at, datetime)
        assert isinstance(ticket.updated_at, datetime)

        # Test that created_at doesn't change on update
        original_created_at = ticket.created_at
        ticket.price = Decimal("129.99")
        ticket.save()
        ticket.refresh_from_db()
        assert ticket.created_at == original_created_at

        # Test that updated_at changes on update
        assert ticket.updated_at > original_created_at

    def test_update_ticket(self):
        """Test updating ticket fields."""
        ticket = self.tickets[1]  # VIP ticket

        # Update fields
        ticket.ticket_type = "Premium VIP"
        ticket.price = Decimal("249.99")
        ticket.save()

        ticket.refresh_from_db()
        assert ticket.ticket_type == "Premium VIP"
        assert ticket.price == Decimal("249.99")

    def test_create_tickets_factory(self):
        """Test creating tickets using EventTicketFactory."""
        # Create new event
        new_event = EventFactory()

        # Create 3 tickets with factory
        factory_tickets = []
        for _ in range(3):
            factory_ticket = EventTicketFactory(event=new_event)
            factory_tickets.append(factory_ticket)

        # Verify tickets were created
        assert EventTicket.objects.filter(event=new_event).count() == 3  # noqa: PLR2004

        # Test basic properties
        for ticket in factory_tickets:
            assert ticket.event == new_event
            assert ticket.ticket_type is not None
            assert ticket.price is not None
            assert ticket.uuid is not None
            assert ticket.created_at is not None
            assert ticket.updated_at is not None
