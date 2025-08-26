from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline

from events.models import Event
from events.models import EventMedia
from events.models import EventParticipant
from events.models import EventTicket
from events.models import SavedEvent


class EventMediaInline(TabularInline):
    """
    Inline admin for EventMedia to be used within EventAdmin.
    """

    model = EventMedia
    extra = 1  # Number of empty forms to display


class EventTicketInline(TabularInline):
    """
    Inline admin for EventTicket to be used within EventAdmin.
    Shows ticket types and prices directly on the Event admin page.
    """

    model = EventTicket
    extra = 1  # Number of empty forms to display


@admin.register(Event)
class EventAdmin(ModelAdmin):
    """
    Admin interface for the Event model.
    """

    list_display = (
        "name",
        "coach",
        "type",
        "location",
        "is_featured",
        "start_datetime",
        "end_datetime",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "description", "short_description", "location")
    list_filter = (
        "type",
        "is_featured",
        "start_datetime",
        "end_datetime",
        "created_at",
    )
    readonly_fields = ("uuid", "slug", "created_at", "updated_at")
    inlines = [EventMediaInline, EventTicketInline]
    autocomplete_fields = ["coach"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "coach",
                    "name",
                    "description",
                    "short_description",
                    "image",
                    "type",
                    "location",
                    "is_featured",
                    "start_datetime",
                    "end_datetime",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "uuid",
                    "slug",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


@admin.register(EventMedia)
class EventMediaAdmin(ModelAdmin):
    """
    Admin interface for the EventMedia model.
    """

    list_display = ("event", "file", "created_at")
    search_fields = ("event__name",)
    list_filter = ("created_at",)
    autocomplete_fields = ["event"]
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)  # Show newest files first
    list_per_page = 20  # Control pagination in admin list view

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "event",
                    "file",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at",),
            },
        ),
    )


@admin.register(EventTicket)
class EventTicketAdmin(ModelAdmin):
    """
    Admin interface for the EventTicket model.
    """

    list_display = ("event", "ticket_type", "price", "created_at", "updated_at")
    search_fields = ("event__name", "ticket_type")
    list_filter = ("created_at", "updated_at")
    autocomplete_fields = ["event"]
    readonly_fields = ("created_at", "updated_at", "uuid")
    ordering = ("-created_at",)
    list_per_page = 20

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "event",
                    "ticket_type",
                    "price",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


@admin.register(EventParticipant)
class EventParticipantAdmin(ModelAdmin):
    """
    Admin interface for the EventParticipant model.
    """

    list_display = ("event", "created_at")
    search_fields = ("event__name", "first_name", "last_name", "phone", "email")
    list_filter = ("created_at",)
    autocomplete_fields = ["event"]
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "event",
                    "first_name",
                    "last_name",
                    "phone",
                    "email",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


@admin.register(SavedEvent)
class SavedEventAdmin(ModelAdmin):
    """
    Admin interface for the SavedEvent model.
    """

    list_display = ("event", "user", "created_at")
    search_fields = ("event__name", "user__name")
    list_filter = ("created_at",)
    autocomplete_fields = ["event", "user"]
    readonly_fields = ("uuid", "created_at")
    ordering = ("-created_at",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "event",
                    "user",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "uuid",
                    "created_at",
                ),
            },
        ),
    )
