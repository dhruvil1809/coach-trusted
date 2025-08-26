from unittest.mock import patch

from django.test import TestCase

from quizzes.models import Quiz
from quizzes.tests.factories import QuizFactory


class QuizSignalsTest(TestCase):
    """Test signals for Quiz model."""

    @patch("quizzes.signals.send_quiz_feedback_email.delay")
    def test_quiz_creation_sends_feedback_email(self, mock_send_email):
        """Test that creating a new quiz triggers feedback email."""
        quiz_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "category": "Business",
            "fields": "Leadership",
            "journey": Quiz.JOURNEY_INTERMEDIATE,
        }

        quiz = Quiz.objects.create(**quiz_data)

        # Assert that the email task was called
        mock_send_email.assert_called_once_with(
            user_email=quiz.email,
            first_name=quiz.first_name,
            last_name=quiz.last_name,
            journey=quiz.journey,
            category=quiz.category,
            fields=quiz.fields,
        )

    @patch("quizzes.signals.send_quiz_feedback_email.delay")
    def test_quiz_update_does_not_send_email(self, mock_send_email):
        """Test that updating an existing quiz does not trigger feedback email."""
        quiz = QuizFactory()

        # Clear any calls from the factory creation
        mock_send_email.reset_mock()

        # Update the quiz
        quiz.first_name = "Updated Name"
        quiz.save()

        # Assert that no email was sent
        mock_send_email.assert_not_called()

    @patch("quizzes.signals.send_quiz_feedback_email.delay")
    def test_quiz_factory_creation_sends_email(self, mock_send_email):
        """Test that QuizFactory creation also triggers feedback email."""
        quiz = QuizFactory(
            first_name="Jane",
            email="jane@example.com",
        )

        # Assert that the email task was called
        mock_send_email.assert_called_once_with(
            user_email=quiz.email,
            first_name=quiz.first_name,
            last_name=quiz.last_name,
            journey=quiz.journey,
            category=quiz.category,
            fields=quiz.fields,
        )
