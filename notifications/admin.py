from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    """
    Admin interface for the Notification model.
    """

    list_display = (
        "id",
        "notification_from",
        "to",
        "truncated_message",
        "reference_type",
        "reference_id",
        "is_read_display",
        "is_deleted_display",
        "created_at",
    )

    list_filter = (
        "is_read",
        "is_deleted",
        "reference_type",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "notification_from__username",
        "notification_from__email",
        "notification_from__first_name",
        "notification_from__last_name",
        "to__username",
        "to__email",
        "to__first_name",
        "to__last_name",
        "message",
        "reference_id",
        "reference_type",
    )

    ordering = ("-created_at",)
    list_per_page = 25

    autocomplete_fields = ["notification_from", "to"]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Notification Details",
            {
                "fields": (
                    "notification_from",
                    "to",
                    "message",
                ),
            },
        ),
        (
            "Reference Information",
            {
                "fields": (
                    "reference_type",
                    "reference_id",
                ),
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_read",
                    "is_deleted",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    actions = [
        "mark_as_read",
        "mark_as_unread",
        "mark_as_deleted",
        "mark_as_not_deleted",
    ]

    # Constants
    MESSAGE_TRUNCATE_LENGTH = 50

    @admin.display(
        description="Message",
    )
    def truncated_message(self, obj):
        """Display truncated message in list view."""
        if len(obj.message) > self.MESSAGE_TRUNCATE_LENGTH:
            return f"{obj.message[: self.MESSAGE_TRUNCATE_LENGTH]}..."
        return obj.message

    @admin.display(
        description="Read Status",
    )
    def is_read_display(self, obj):
        """Display read status with colored indicator."""
        if obj.is_read:
            return format_html(
                '<span style="color: green;">✓ Read</span>',
            )
        return format_html(
            '<span style="color: orange;">● Unread</span>',
        )

    @admin.display(
        description="Status",
    )
    def is_deleted_display(self, obj):
        """Display deleted status with colored indicator."""
        if obj.is_deleted:
            return format_html(
                '<span style="color: red;">🗑 Deleted</span>',
            )
        return format_html(
            '<span style="color: green;">✓ Active</span>',
        )

    @admin.action(
        description="Mark selected notifications as read",
    )
    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        updated = queryset.update(is_read=True)
        self.message_user(
            request,
            f"{updated} notification(s) marked as read.",
        )

    @admin.action(
        description="Mark selected notifications as unread",
    )
    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread."""
        updated = queryset.update(is_read=False)
        self.message_user(
            request,
            f"{updated} notification(s) marked as unread.",
        )

    @admin.action(
        description="Mark selected notifications as deleted",
    )
    def mark_as_deleted(self, request, queryset):
        """Mark selected notifications as deleted."""
        updated = queryset.update(is_deleted=True)
        self.message_user(
            request,
            f"{updated} notification(s) marked as deleted.",
        )

    @admin.action(
        description="Restore selected notifications",
    )
    def mark_as_not_deleted(self, request, queryset):
        """Mark selected notifications as not deleted."""
        updated = queryset.update(is_deleted=False)
        self.message_user(
            request,
            f"{updated} notification(s) restored.",
        )
