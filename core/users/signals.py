from django.db.models.signals import post_delete
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Profile


@receiver(pre_save, sender=Profile)
def delete_old_profile_picture(sender, instance, **kwargs):
    """
    Signal handler that deletes the old profile picture when a new one is uploaded.
    This function is triggered when a Profile model instance is about to be saved.
    It checks if the profile picture has been changed, and if so, deletes the old
    profile picture file to prevent unused files from accumulating in storage.
    Parameters:
        sender (Model): The model class sending the signal.
        instance (Profile): The Profile instance being saved.
        **kwargs: Additional keyword arguments passed by the signal.
    Returns:
        None
    """

    if not instance.pk:
        # New instance, so no old picture to delete
        return

    try:
        old_instance = Profile.objects.get(pk=instance.pk)
    except Profile.DoesNotExist:
        return

    # Check if profile picture has changed
    if (
        old_instance.profile_picture
        and old_instance.profile_picture != instance.profile_picture
    ):
        # Delete the old profile picture file
        old_instance.profile_picture.delete(save=False)


@receiver(post_delete, sender=Profile)
def delete_profile_picture_on_delete(sender, instance, **kwargs):
    """
    Signal handler that deletes a user's profile picture file when the user instance is deleted.
    This function is intended to be connected to the pre_delete signal of the User model.
    It checks if the user has a profile picture and deletes the associated file from storage
    to prevent orphaned files when a user is deleted.
    Args:
        sender (Model): The model class that sent the signal.
        instance (User): The instance of the User model that is about to be deleted.
        **kwargs: Additional keyword arguments passed by the signal.
    Returns:
        None
    """  # noqa: E501

    if instance.profile_picture:
        instance.profile_picture.delete(save=False)
