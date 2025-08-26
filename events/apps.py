from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "events"

    def ready(self):
        """
        This method is called when the application is ready.
        It can be used to perform any initialization tasks.
        """
        # Import signal handlers
        import events.signals  # noqa: F401
