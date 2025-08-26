from django.db import models


class Quiz(models.Model):
    JOURNEY_BEGINNER = "beginner"
    JOURNEY_INTERMEDIATE = "intermediate"
    JOURNEY_EXPERT = "expert"
    JOURNEY_CHOICES = [
        (JOURNEY_BEGINNER, "Beginner"),
        (JOURNEY_INTERMEDIATE, "Intermediate"),
        (JOURNEY_EXPERT, "Expert"),
    ]

    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    email = models.EmailField(max_length=255, verbose_name="Email Address")
    category = models.CharField(max_length=255, verbose_name="Category")
    fields = models.CharField(max_length=255, verbose_name="Fields")
    journey = models.CharField(
        max_length=255,
        choices=JOURNEY_CHOICES,
        default=JOURNEY_BEGINNER,
        verbose_name="Journey Level",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.fields} - {self.journey}"


class Fields(models.Model):
    name = models.CharField(max_length=100, verbose_name="Field Name")
    description = models.TextField(
        verbose_name="Field Description",
        default="",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
