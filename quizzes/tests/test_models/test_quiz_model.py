from unittest.mock import patch

from django.test import TestCase

from quizzes.models import Quiz
from quizzes.tests.factories import FieldsFactory
from quizzes.tests.factories import QuizFactory


class FieldsModelTest(TestCase):
    def test_str(self):
        field = FieldsFactory(name="Test Field")
        assert str(field) == "Test Field"


class QuizModelTest(TestCase):
    @patch("quizzes.signals.send_quiz_feedback_email.delay")
    def test_str(self, mock_send_email):
        quiz = QuizFactory(
            first_name="John",
            last_name="Doe",
            journey=Quiz.JOURNEY_EXPERT,
        )
        s = str(quiz)
        assert "John" in s
        assert "Doe" in s
        assert str(quiz.fields) in s
        assert quiz.journey in s

    @patch("quizzes.signals.send_quiz_feedback_email.delay")
    def test_quiz_fields(self, mock_send_email):
        quiz = QuizFactory()
        assert quiz.first_name
        assert quiz.last_name
        assert quiz.email
        assert quiz.category is not None
        assert quiz.fields is not None
        assert quiz.journey in [
            quiz.JOURNEY_BEGINNER,
            quiz.JOURNEY_INTERMEDIATE,
            quiz.JOURNEY_EXPERT,
        ]
