from django.apps import AppConfig


class CoachConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coach"

    def ready(self):
        """
        Import and register signal handlers when the app is ready.
        """
        import coach.signals  # noqa: F401
