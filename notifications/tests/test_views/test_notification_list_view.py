import pytest
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.users.tests.factories import UserFactory
from notifications.tests.factories import UnreadNotificationFactory


@pytest.mark.django_db
class NotificationListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.list_url = reverse("notifications:list")
        self.user = UserFactory()
        self.sender = UserFactory()

    def test_get_notification_list(self):
        """Test getting list of notifications"""
        # Create test notifications
        UnreadNotificationFactory(
            to=self.user,
            notification_from=self.sender,
            message="First notification",
        )
        UnreadNotificationFactory(
            to=self.user,
            notification_from=self.sender,
            message="Second notification",
        )

        self.client.force_login(self.user)
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "results" in data
        assert len(data["results"]) == 2  # noqa: PLR2004

    def test_notification_list_sorting(self):
        """Test notification list sorting by created_at"""
        # Create notifications
        UnreadNotificationFactory(
            to=self.user,
            notification_from=self.sender,
            message="First notification",
        )
        UnreadNotificationFactory(
            to=self.user,
            notification_from=self.sender,
            message="Second notification",
        )

        self.client.force_login(self.user)

        # Test default sorting (newest first)
        response = self.client.get(self.list_url)
        data = response.json()
        results = data["results"]

        assert results[0]["message"] == "Second notification"
        assert results[1]["message"] == "First notification"

        # Test ascending order
        response = self.client.get(self.list_url + "?ordering=created_at")
        data = response.json()
        results = data["results"]

        assert results[0]["message"] == "First notification"
        assert results[1]["message"] == "Second notification"
