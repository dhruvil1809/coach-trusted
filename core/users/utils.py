import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_verification_email(email, code):
    """Send verification email."""
    try:
        logger.info(f"Sending verification email to {email}")  # noqa: G004
        send_mail(
            "Your Verification Code",
            f"Your verification code is {code}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
        logger.info(f"Your verification code is {code}")  # noqa: G004
    except Exception as e:
        logger.exception(f"Failed to send verification email to {email}: {e}")  # noqa: G004, TRY401
