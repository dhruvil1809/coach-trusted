from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory

from core.users.tests.factories import UserFactory
from notifications.models import Notification


class NotificationFactory(DjangoModelFactory):
    """Factory for creating Notification instances for testing."""

    notification_from = SubFactory(UserFactory)
    to = SubFactory(UserFactory)
    message = Faker("text", max_nb_chars=200)

    is_read = Faker("boolean", chance_of_getting_true=30)
    is_deleted = Faker("boolean", chance_of_getting_true=10)

    reference_id = Faker("uuid4")
    reference_type = Faker(
        "random_element",
        elements=["coach", "product", "event", "quiz", "inquiry", "review"],
    )

    class Meta:
        model = Notification


class ReadNotificationFactory(NotificationFactory):
    """Factory for creating read notifications."""

    is_read = True
    is_deleted = False


class UnreadNotificationFactory(NotificationFactory):
    """Factory for creating unread notifications."""

    is_read = False
    is_deleted = False


class DeletedNotificationFactory(NotificationFactory):
    """Factory for creating deleted notifications."""

    is_deleted = True


class CoachNotificationFactory(NotificationFactory):
    """Factory for creating coach-related notifications."""

    reference_type = "coach"
    message = Faker(
        "random_element",
        elements=[
            "Your coach profile has been updated successfully.",
            "A new review has been posted for your coaching services.",
            "Your coaching session has been scheduled.",
            "Your coach verification is pending approval.",
            "Your coaching profile has been approved.",
        ],
    )


class ProductNotificationFactory(NotificationFactory):
    """Factory for creating product-related notifications."""

    reference_type = "product"
    message = Faker(
        "random_element",
        elements=[
            "Your product has been purchased.",
            "Your product listing has been updated.",
            "A new review has been posted for your product.",
            "Your product has been approved for sale.",
            "Your product listing is pending approval.",
        ],
    )


class EventNotificationFactory(NotificationFactory):
    """Factory for creating event-related notifications."""

    reference_type = "event"
    message = Faker(
        "random_element",
        elements=[
            "You have been registered for the event.",
            "The event you registered for has been updated.",
            "Reminder: Your event starts in 1 hour.",
            "The event has been cancelled.",
            "You have successfully checked in to the event.",
        ],
    )


class QuizNotificationFactory(NotificationFactory):
    """Factory for creating quiz-related notifications."""

    reference_type = "quiz"
    message = Faker(
        "random_element",
        elements=[
            "You have completed the quiz successfully.",
            "Your quiz results are now available.",
            "A new quiz has been assigned to you.",
            "Quiz deadline reminder: 2 days remaining.",
            "You have achieved a new quiz milestone.",
        ],
    )


class InquiryNotificationFactory(NotificationFactory):
    """Factory for creating inquiry-related notifications."""

    reference_type = "inquiry"
    message = Faker(
        "random_element",
        elements=[
            "You have received a new inquiry.",
            "Your inquiry has been responded to.",
            "Your inquiry status has been updated.",
            "Your inquiry has been resolved.",
            "Follow-up required for your inquiry.",
        ],
    )


class ReviewNotificationFactory(NotificationFactory):
    """Factory for creating review-related notifications."""

    reference_type = "review"
    message = Faker(
        "random_element",
        elements=[
            "You have received a new review.",
            "Your review has been published.",
            "A review you wrote has been liked.",
            "Your review has been reported.",
            "Thank you for your honest review.",
        ],
    )
