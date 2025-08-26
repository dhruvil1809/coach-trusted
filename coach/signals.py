from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import ClaimCoachRequest
from .tasks import send_coach_claim_approval_email
from .tasks import send_coach_claim_rejection_email


@receiver(pre_save, sender=ClaimCoachRequest)
def handle_claim_coach_request_status_change(sender, instance, **kwargs):
    """
    Signal handler that sends notifications when a ClaimCoachRequest's status changes.

    This handler checks if a ClaimCoachRequest has been approved or rejected and
    triggers the appropriate Celery task to send an email notification to the user.

    Args:
        sender: The model class that sent the signal (ClaimCoachRequest)
        instance: The actual instance being saved
        **kwargs: Additional keyword arguments
    """
    # Skip for new instances
    if instance.pk:
        try:
            # Get the previous state of the instance from the database
            old_instance = ClaimCoachRequest.objects.get(pk=instance.pk)

            # Only send emails when the status field changes
            if old_instance.status != instance.status:
                # For approved requests
                if (
                    instance.status == ClaimCoachRequest.STATUS_APPROVED
                    and instance.user
                ):
                    coach_name = f"{instance.coach.first_name} {instance.coach.last_name}".strip()  # noqa: E501
                    send_coach_claim_approval_email.delay(
                        user_email=instance.email,
                        first_name=instance.first_name,
                        coach_name=coach_name,
                        approval_reason=instance.approval_reason,
                    )

                # For rejected requests
                elif (
                    instance.status == ClaimCoachRequest.STATUS_REJECTED
                    and instance.user
                ):
                    coach_name = f"{instance.coach.first_name} {instance.coach.last_name}".strip()  # noqa: E501
                    send_coach_claim_rejection_email.delay(
                        user_email=instance.email,
                        first_name=instance.first_name,
                        coach_name=coach_name,
                        rejection_reason=instance.rejection_reason,
                    )
        except ClaimCoachRequest.DoesNotExist:
            pass
