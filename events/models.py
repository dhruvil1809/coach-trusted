import uuid

from django.db import models
from django.utils.text import slugify

from coach.models import Coach
from core.users.models import User


def get_event_image_upload_path(instance, filename):
    """
    Generates a file upload path for event images.

    The function creates a unique filename using a UUID and retains the original file extension.
    The resulting path is structured as 'events/images/<unique_filename>'.

    Args:
        instance: The model instance this file is associated with.
        filename (str): The original name of the uploaded file.

    Returns:
        str: The upload path for the event image.
    """  # noqa: E501

    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"events/images/{filename}"


def get_event_media_upload_path(instance, filename):
    """
    Generates a file upload path for event media files.

    The function creates a unique filename using a UUID and retains the original file extension.
    The resulting path is structured as 'events/media/<unique_filename>'.

    Args:
        instance: The model instance this file is associated with.
        filename (str): The original name of the uploaded file.

    Returns:
        str: The upload path for the event media file.
    """  # noqa: E501

    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"events/media/{filename}"


class Event(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    slug = models.SlugField(max_length=500, unique=True)

    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name="events")
    name = models.CharField(max_length=500)
    description = models.TextField()
    short_description = models.TextField(blank=True)
    image = models.ImageField(upload_to=get_event_image_upload_path)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    type = models.CharField(
        max_length=255,
        choices=[
            ("online", "Online Event"),
            ("offline", "Offline Event"),
        ],
        default="online",
    )
    location = models.CharField(max_length=500, blank=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.name)}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class EventMedia(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to=get_event_media_upload_path)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event.name} - {self.file.name}"


class EventTicket(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    ticket_type = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event.name} - {self.ticket_type}"


class EventParticipant(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="participants",
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event.name} - {self.first_name} {self.last_name}"


class SavedEvent(models.Model):
    """
    Model to save events for users.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="saved_events",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_events",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "user")
        verbose_name = "Saved Event"
        verbose_name_plural = "Saved Events"

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"
