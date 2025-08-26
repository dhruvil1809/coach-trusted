from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task()
def send_quiz_feedback_email(  # noqa: PLR0913
    user_email,
    first_name,
    last_name,
    journey,
    category,
    fields,
):
    """
    Send a feedback email to a user who just completed a quiz.

    Args:
        user_email (str): The email address of the user who completed the quiz
        first_name (str): The first name of the user
        last_name (str): The last name of the user
        journey (str): The journey level (beginner, intermediate, expert)
        category (str): The category selected in the quiz
        fields (str): The fields selected in the quiz
    """
    context = {
        "first_name": first_name,
        "last_name": last_name,
        "journey": journey,
        "category": category,
        "fields": fields,
    }

    subject = "Thank you for completing your coaching quiz!"

    # Try to render HTML template first, fallback to plain text if not found
    try:
        html_message = render_to_string("emails/quizzes/quiz_feedback.html", context)
        message = render_to_string("emails/quizzes/quiz_feedback.txt", context)
    except Exception:  # noqa: BLE001
        # Fallback to plain text message if templates don't exist
        message = f"""
        Hello {first_name},

        Thank you for completing our coaching quiz! We're excited to help you on
        your {journey} journey.

        Based on your responses:
        - Journey Level: {journey.title()}
        - Category: {category}
        - Fields of Interest: {fields}

        Our team will review your information and connect you with coaches who
        match your needs and goals.

        You can expect to hear from us soon with personalized coach recommendations.

        If you have any questions in the meantime, please don't hesitate to reach
        out to our support team.

        Best regards,
        The Coach Trusted Team
        """.strip()
        html_message = None

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
        html_message=html_message,
    )
