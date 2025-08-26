from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from coach.models import Category
from quizzes.models import Quiz
from quizzes.tests.factories import FieldsFactory


class QuizCreateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.fields = FieldsFactory()
        self.category = Category.objects.first() or Category.objects.create(
            name="Test Category",
        )
        self.url = reverse("quizzes:quiz-create")

    def test_quiz_create_view(self):
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "category": self.category.name,
            "fields": self.fields.name,
            "journey": Quiz.JOURNEY_BEGINNER,
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        quiz = Quiz.objects.get(email="jane@example.com")
        assert quiz.first_name == "Jane"
        assert quiz.last_name == "Smith"
        assert quiz.fields == self.fields.name
        assert quiz.category == self.category.name
        assert quiz.journey == Quiz.JOURNEY_BEGINNER
