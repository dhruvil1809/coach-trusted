from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task()
def send_coach_claim_approval_email(
    user_email,
    first_name,
    coach_name,
    approval_reason,
):
    """
    Send an email to notify a user that their coach claim request has been approved.

    Args:
        user_email (str): The email address of the user to send the notification to
        first_name (str): The first name of the user
        coach_name (str): The name of the coach profile that was claimed
        approval_reason (str): The reason provided for the approval
    """
    subject = f"Your claim request for {coach_name} has been approved"
    message = f"""
    Hello {first_name},

    Great news! Your request to claim the coach profile for {coach_name} has been approved.

    Approval reason: {approval_reason}

    You can now manage your coach profile through your account.

    Best regards,
    The Coach Trusted Team
    """  # noqa: E501

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )


@shared_task()
def send_coach_claim_rejection_email(
    user_email,
    first_name,
    coach_name,
    rejection_reason,
):
    """
    Send an email to notify a user that their coach claim request has been rejected.

    Args:
        user_email (str): The email address of the user to send the notification to
        first_name (str): The first name of the user
        coach_name (str): The name of the coach profile that was requested
        rejection_reason (str): The reason provided for the rejection
    """
    subject = f"Your claim request for {coach_name} has been rejected"
    message = f"""
    Hello {first_name},

    We regret to inform you that your request to claim the coach profile for {coach_name} has been rejected.

    Rejection reason: {rejection_reason}

    If you believe this is in error or would like to provide additional information, please contact our support team.

    Best regards,
    The Coach Trusted Team
    """  # noqa: E501

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
