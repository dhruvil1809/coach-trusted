from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import ProductMedia


@receiver(post_delete, sender=ProductMedia)
def delete_media_file_on_delete(sender, instance, **kwargs):
    """
    Delete the media file from storage when a ProductMedia instance is deleted.
    """
    if instance.media_file:
        try:  # noqa: SIM105
            # Delete the file from storage
            instance.media_file.delete(
                False,  # noqa: FBT003
            )  # False means don't save the model
        except Exception:  # noqa: BLE001, S110
            pass
