from unittest.mock import patch

from django.test import TestCase
from django.test import override_settings

from quizzes.tasks import send_quiz_feedback_email


class QuizTasksTest(TestCase):
    """Test tasks for Quiz app."""

    @patch("quizzes.tasks.send_mail")
    @patch("quizzes.tasks.render_to_string")
    def test_send_quiz_feedback_email_with_templates(
        self,
        mock_render_to_string,
        mock_send_mail,
    ):
        """Test sending feedback email when templates exist."""
        # Mock template rendering
        mock_render_to_string.side_effect = [
            "<html>Test HTML</html>",  # HTML template
            "Test plain text",  # Text template
        ]

        send_quiz_feedback_email(
            user_email="test@example.com",
            first_name="John",
            last_name="Doe",
            journey="intermediate",
            category="Business",
            fields="Leadership",
        )

        # Assert templates were rendered (HTML and text)
        expected_template_calls = 2
        assert mock_render_to_string.call_count == expected_template_calls
        mock_render_to_string.assert_any_call(
            "emails/quizzes/quiz_feedback.html",
            {
                "first_name": "John",
                "last_name": "Doe",
                "journey": "intermediate",
                "category": "Business",
                "fields": "Leadership",
            },
        )
        mock_render_to_string.assert_any_call(
            "emails/quizzes/quiz_feedback.txt",
            {
                "first_name": "John",
                "last_name": "Doe",
                "journey": "intermediate",
                "category": "Business",
                "fields": "Leadership",
            },
        )

        # Assert email was sent
        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args
        assert kwargs["subject"] == "Thank you for completing your coaching quiz!"
        assert kwargs["message"] == "Test plain text"
        assert kwargs["recipient_list"] == ["test@example.com"]
        assert kwargs["html_message"] == "<html>Test HTML</html>"

    @patch("quizzes.tasks.send_mail")
    @patch("quizzes.tasks.render_to_string")
    def test_send_quiz_feedback_email_fallback(
        self,
        mock_render_to_string,
        mock_send_mail,
    ):
        """Test sending feedback email when templates don't exist."""
        # Mock template rendering to raise an exception
        mock_render_to_string.side_effect = Exception("Template not found")

        send_quiz_feedback_email(
            user_email="test@example.com",
            first_name="John",
            last_name="Doe",
            journey="beginner",
            category="Health",
            fields="Fitness",
        )

        # Assert email was sent with fallback message
        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args
        assert kwargs["subject"] == "Thank you for completing your coaching quiz!"
        assert "Hello John" in kwargs["message"]
        assert "beginner journey" in kwargs["message"]
        assert "Health" in kwargs["message"]
        assert "Fitness" in kwargs["message"]
        assert kwargs["recipient_list"] == ["test@example.com"]
        assert kwargs["html_message"] is None

    @override_settings(DEFAULT_FROM_EMAIL="noreply@coachtrusted.com")
    @patch("quizzes.tasks.send_mail")
    @patch("quizzes.tasks.render_to_string")
    def test_send_quiz_feedback_email_uses_correct_from_email(
        self,
        mock_render_to_string,
        mock_send_mail,
    ):
        """Test that the correct from_email is used."""
        mock_render_to_string.side_effect = Exception("Template not found")

        send_quiz_feedback_email(
            user_email="test@example.com",
            first_name="John",
            last_name="Doe",
            journey="expert",
            category="Technology",
            fields="Software Development",
        )

        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args
        assert kwargs["from_email"] == "noreply@coachtrusted.com"
