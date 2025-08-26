import factory

from quizzes.models import Fields
from quizzes.models import Quiz


class FieldsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Fields
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Field {n}")
    description = factory.Faker("sentence")


class QuizFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quiz
        django_get_or_create = (
            "first_name",
            "last_name",
            "email",
            "category",
            "fields",
            "journey",
        )

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    category = factory.Faker("word")
    fields = factory.Faker("word")  # Changed from SubFactory to generate string
    journey = factory.Iterator(
        [Quiz.JOURNEY_BEGINNER, Quiz.JOURNEY_INTERMEDIATE, Quiz.JOURNEY_EXPERT],
    )
