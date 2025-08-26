from django.apps import AppConfig


class QuizzesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "quizzes"

    def ready(self):
        """
        Import and register signal handlers when the app is ready.
        """
        import quizzes.signals  # noqa: F401
