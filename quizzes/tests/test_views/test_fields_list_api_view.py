from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from quizzes.tests.factories import FieldsFactory


class FieldsListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("quizzes:fields-list")

    def test_fields_list_view(self):
        # Create test fields
        _ = FieldsFactory(name="Business Coaching")
        _ = FieldsFactory(name="Life Coaching")
        _ = FieldsFactory(name="Career Coaching")

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3  # noqa: PLR2004

        # Check that all fields are returned
        field_names = [field["name"] for field in response.data]
        assert "Business Coaching" in field_names
        assert "Life Coaching" in field_names
        assert "Career Coaching" in field_names

    def test_fields_list_ordering_by_name(self):
        # Create fields in reverse alphabetical order
        FieldsFactory(name="Zebra Coaching")
        FieldsFactory(name="Alpha Coaching")
        FieldsFactory(name="Beta Coaching")

        response = self.client.get(self.url, {"ordering": "name"})
        assert response.status_code == status.HTTP_200_OK

        # Check ordering
        names = [field["name"] for field in response.data]
        assert names == ["Alpha Coaching", "Beta Coaching", "Zebra Coaching"]

    def test_fields_list_ordering_by_id(self):
        _ = FieldsFactory(name="First")
        _ = FieldsFactory(name="Second")

        response = self.client.get(self.url, {"ordering": "id"})
        assert response.status_code == status.HTTP_200_OK

        # Check ordering by id
        ids = [field["id"] for field in response.data]
        assert ids[0] < ids[1]
