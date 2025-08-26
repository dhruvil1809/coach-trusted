from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SerializerMethodField

from coach.serializers.coach import CoachDetailSerializer
from coach.serializers.coach import CoachListSerializer

from .models import Event
from .models import EventMedia
from .models import EventTicket
from .models import SavedEvent


class EventTicketEventListSerializer(ModelSerializer):
    class Meta:
        model = EventTicket
        fields = ("id", "uuid", "ticket_type", "price")


class EventListSerializer(ModelSerializer):
    coach = CoachListSerializer()
    tickets = SerializerMethodField()

    is_saved = serializers.SerializerMethodField(
        read_only=True,
        help_text="Indicates if the event is saved by the user",
    )

    is_saved_uuid = serializers.SerializerMethodField(
        read_only=True,
        help_text="UUID of the saved event record if saved by the user",
    )

    def get_tickets(self, obj):
        ordered_tickets = obj.tickets.all().order_by(
            "price",
        )  # Order by price ascending
        return EventTicketEventListSerializer(ordered_tickets, many=True).data

    class Meta:
        model = Event
        fields = (
            "id",
            "uuid",
            "slug",
            "name",
            "image",
            "short_description",
            "start_datetime",
            "end_datetime",
            "type",
            "location",
            "is_featured",
            "is_saved",
            "is_saved_uuid",
            "created_at",
            "updated_at",
            "tickets",
            "coach",
        )

    def get_is_saved(self, obj):
        request = self.context.get("request")
        if not request:
            return False

        user = request.user if request.user else None
        if user and user.is_authenticated:
            return SavedEvent.objects.filter(
                event=obj,
                user=user,
            ).exists()

        return False

    def get_is_saved_uuid(self, obj):
        request = self.context.get("request")
        if not request:
            return None

        user = request.user if request.user else None
        if user and user.is_authenticated:
            try:
                saved_event = SavedEvent.objects.get(
                    event=obj,
                    user=user,
                )
                return str(saved_event.uuid)
            except SavedEvent.DoesNotExist:
                return None

        return None


class EventMediaEventDetailSerializer(ModelSerializer):
    class Meta:
        model = EventMedia
        fields = ("id", "file", "created_at")
        read_only_fields = ("id", "file")


class EventDetailSerializer(ModelSerializer):
    coach = CoachDetailSerializer()
    tickets = SerializerMethodField()
    media = EventMediaEventDetailSerializer(many=True)

    is_saved = serializers.SerializerMethodField(
        read_only=True,
        help_text="Indicates if the event is saved by the user",
    )

    is_saved_uuid = serializers.SerializerMethodField(
        read_only=True,
        help_text="UUID of the saved event record if saved by the user",
    )

    def get_tickets(self, obj):
        ordered_tickets = obj.tickets.all().order_by(
            "price",
        )  # Order by price ascending
        return EventTicketEventListSerializer(ordered_tickets, many=True).data

    class Meta:
        model = Event
        fields = (
            "id",
            "uuid",
            "slug",
            "name",
            "image",
            "description",
            "short_description",
            "start_datetime",
            "end_datetime",
            "is_featured",
            "is_saved",
            "is_saved_uuid",
            "created_at",
            "updated_at",
            "type",
            "location",
            "tickets",
            "media",
            "coach",
        )

    def get_is_saved(self, obj):
        request = self.context.get("request")
        if not request:
            return False

        user = request.user if request.user else None
        if user and user.is_authenticated:
            return SavedEvent.objects.filter(
                event=obj,
                user=user,
            ).exists()

        return False

    def get_is_saved_uuid(self, obj):
        request = self.context.get("request")
        if not request:
            return None

        user = request.user if request.user else None
        if user and user.is_authenticated:
            try:
                saved_event = SavedEvent.objects.get(
                    event=obj,
                    user=user,
                )
                return str(saved_event.uuid)
            except SavedEvent.DoesNotExist:
                return None

        return None


class SavedEventListSerializer(ModelSerializer):
    event = EventListSerializer()

    class Meta:
        model = SavedEvent
        fields = ("uuid", "event", "created_at")
        read_only_fields = ("uuid", "event", "created_at")


class AddSavedEventSerializer(serializers.Serializer):
    event_uuid = serializers.UUIDField(required=True)
