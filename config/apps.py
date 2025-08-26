from django.apps import AppConfig


class ConfigConfig(AppConfig):
    name = "config"

    def ready(self):
        """Import the celery beat admin configuration when the app is ready."""
        # Import the celery beat admin to register the custom admin classes
        import config.celery_beat_admin  # noqa: F401
