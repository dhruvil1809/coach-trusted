from django.db.models.signals import post_delete
from django.dispatch import receiver

from events.models import EventMedia


@receiver(post_delete, sender=EventMedia)
def delete_event_media_file_on_delete(sender, instance, **kwargs):
    """
    Delete the media file from storage when an EventMedia instance is deleted.
    This handler ensures files are deleted even during bulk delete operations.
    """
    if instance.file:
        try:  # noqa: SIM105
            # Delete the file from storage without saving the model
            instance.file.delete(False)  # noqa: FBT003
        except Exception:  # noqa: BLE001, S110
            # Silent pass if file deletion fails (e.g., file already gone)
            pass
