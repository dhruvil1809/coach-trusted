from rest_framework import serializers

from core.users.serializers import UserListWithProfileSerializer
from notifications.models import Notification


class NotificationListSerializer(serializers.ModelSerializer):
    from_user = UserListWithProfileSerializer(
        source="notification_from",
        read_only=True,
    )

    class Meta:
        model = Notification
        fields = [
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


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notification status"""

    class Meta:
        model = Notification
        fields = ["is_read", "is_deleted"]

    def validate(self, attrs):
        """Validate that at least one field is being updated"""
        if not attrs:
            msg = "At least one field (is_read or is_deleted) must be provided"
            raise serializers.ValidationError(msg)
        return attrs
