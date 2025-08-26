from django.db import models

from core.users.models import User


class Notification(models.Model):
    notification_from = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications_sent",
    )
    to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications_received",
    )
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    reference_id = models.CharField(max_length=255, blank=True)
    reference_type = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification from {self.notification_from.username} to {self.to.username} - {'Read' if self.is_read else 'Unread'}"  # noqa: E501
