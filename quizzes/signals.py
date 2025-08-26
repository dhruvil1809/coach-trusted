from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Quiz
from .tasks import send_quiz_feedback_email


@receiver(post_save, sender=Quiz)
def handle_quiz_creation(sender, instance, created, **kwargs):
    """
    Signal handler that sends a feedback email when a new quiz is created.

    This handler triggers a Celery task to send a feedback email to the user
    who just completed the quiz.

    Args:
        sender: The model class that sent the signal (Quiz)
        instance: The actual Quiz instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    # Only send email for newly created quiz instances
    if created:
        send_quiz_feedback_email.delay(
            user_email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            journey=instance.journey,
            category=instance.category,
            fields=instance.fields,
        )
