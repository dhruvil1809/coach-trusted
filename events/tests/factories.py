import uuid
from datetime import timedelta
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from factory import Faker
from factory import LazyAttribute
from factory import SubFactory
from factory import post_generation
from factory.django import DjangoModelFactory
from PIL import Image

from coach.tests.factories import CoachFactory
from core.users.tests.factories import UserFactory
from events.models import Event
from events.models import EventMedia
from events.models import EventParticipant
from events.models import EventTicket
from events.models import SavedEvent


def create_test_image(filename="event.jpg", size=(100, 100), color="red"):
    """Helper function to create test image files for events"""
    image_file = BytesIO()
    image = Image.new("RGB", size=size, color=color)
    image.save(image_file, "JPEG")
    image_file.seek(0)

    return SimpleUploadedFile(
        name=filename,
        content=image_file.read(),
        content_type="image/jpeg",
    )


def create_test_file(filename="event_document.pdf", content=b"test content"):
    """Helper function to create test files for event media"""
    return SimpleUploadedFile(
        name=filename,
        content=content,
        content_type="application/pdf",
    )


class EventFactory(DjangoModelFactory):
    """Factory for the Event model."""

    uuid = LazyAttribute(lambda _: uuid.uuid4())
    coach = SubFactory(CoachFactory)
    name = Faker("sentence", nb_words=4)
    description = Faker("paragraph")
    short_description = Faker("sentence", nb_words=10)
    start_datetime = LazyAttribute(lambda _: timezone.now() + timedelta(days=1))
    end_datetime = LazyAttribute(lambda obj: obj.start_datetime + timedelta(hours=2))
    type = "online"
    location = Faker("address")
    is_featured = False  # Default to False for consistent testing

    @post_generation
    def image(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.image = extracted
        else:
            self.image = create_test_image("event.jpg")

    class Meta:
        model = Event


class EventMediaFactory(DjangoModelFactory):
    """Factory for the EventMedia model."""

    event = SubFactory(EventFactory)

    @post_generation
    def file(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.file = extracted
        else:
            self.file = create_test_file("event_media.pdf")

    class Meta:
        model = EventMedia


class EventTicketFactory(DjangoModelFactory):
    """Factory for the EventTicket model."""

    event = SubFactory(EventFactory)
    ticket_type = Faker("word")
    price = Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    uuid = LazyAttribute(lambda _: uuid.uuid4())

    class Meta:
        model = EventTicket


class EventParticipantFactory(DjangoModelFactory):
    """Factory for the EventParticipant model."""

    event = SubFactory(EventFactory)
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    phone = Faker("phone_number")
    email = Faker("email")
    uuid = LazyAttribute(lambda _: uuid.uuid4())

    class Meta:
        model = EventParticipant


class SavedEventFactory(DjangoModelFactory):
    """Factory for the SavedEvent model."""

    event = SubFactory(EventFactory)
    user = SubFactory(UserFactory)
    uuid = LazyAttribute(lambda _: uuid.uuid4())

    class Meta:
        model = SavedEvent
        django_get_or_create = ("event", "user")


class UserWithSavedEventsFactory(UserFactory):
    """Factory for User with saved events."""

    @post_generation
    def saved_events(self, create, extracted, **kwargs):
        if not create:
            return

        # If an explicit number is specified, create that many saved events
        count = extracted if extracted is not None else 10
        SavedEventFactory.create_batch(count, user=self)
