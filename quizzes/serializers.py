from rest_framework import serializers

from .models import Fields
from .models import Quiz


class FieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fields
        fields = [
            "id",
            "name",
        ]


class QuizCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "category",
            "fields",
            "journey",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
