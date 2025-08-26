import pytest
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.users.tests.factories import UserFactory
from notifications.tests.factories import UnreadNotificationFactory


@pytest.mark.django_db
class NotificationUpdateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.sender = UserFactory()

        self.notification = UnreadNotificationFactory(
            to=self.user,
            notification_from=self.sender,
            message="Test notification",
        )

        self.update_url = reverse(
            "notifications:update",
            kwargs={"id": self.notification.id},
        )

    def test_mark_notification_as_read(self):
        """Test marking a notification as read"""
        self.client.force_login(self.user)

        data = {"is_read": True}
        response = self.client.patch(
            self.update_url,
            data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["is_read"] is True
        assert response_data["is_deleted"] is False

        # Verify in database
        self.notification.refresh_from_db()
        assert self.notification.is_read is True
        assert self.notification.is_deleted is False

    def test_mark_notification_as_deleted(self):
        """Test marking a notification as deleted"""
        self.client.force_login(self.user)

        data = {"is_deleted": True}
        response = self.client.patch(
            self.update_url,
            data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["is_read"] is False
        assert response_data["is_deleted"] is True

        # Verify in database
        self.notification.refresh_from_db()
        assert self.notification.is_read is False
        assert self.notification.is_deleted is True

    def test_mark_notification_as_read_and_deleted(self):
        """Test marking a notification as both read and deleted"""
        self.client.force_login(self.user)

        data = {"is_read": True, "is_deleted": True}
        response = self.client.patch(
            self.update_url,
            data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["is_read"] is True
        assert response_data["is_deleted"] is True

        # Verify in database
        self.notification.refresh_from_db()
        assert self.notification.is_read is True
        assert self.notification.is_deleted is True

    def test_update_notification_empty_data(self):
        """Test updating notification with empty data should fail"""
        self.client.force_login(self.user)

        data = {}
        response = self.client.patch(
            self.update_url,
            data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()

        assert "At least one field" in str(response_data)

    def test_update_notification_unauthenticated(self):
        """Test updating notification without authentication should fail"""
        data = {"is_read": True}
        response = self.client.patch(
            self.update_url,
            data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_notification_wrong_user(self):
        """Test updating notification by wrong user should fail"""
        self.client.force_login(self.other_user)

        data = {"is_read": True}
        response = self.client.patch(
            self.update_url,
            data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_nonexistent_notification(self):
        """Test updating a non-existent notification should fail"""
        self.client.force_login(self.user)

        nonexistent_url = reverse(
            "notifications:update",
            kwargs={"id": 99999},
        )
        data = {"is_read": True}
        response = self.client.patch(
            nonexistent_url,
            data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_response_includes_full_notification_data(self):
        """Test that response includes all notification fields"""
        self.client.force_login(self.user)

        data = {"is_read": True}
        response = self.client.patch(
            self.update_url,
            data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        # Check that all expected fields are present
        expected_fields = [
            "id",
            "message",
            "is_read",
            "is_deleted",
            "reference_id",
            "reference_type",
            "created_at",
            "updated_at",
            "from_user",
        ]

        for field in expected_fields:
            assert field in response_data
