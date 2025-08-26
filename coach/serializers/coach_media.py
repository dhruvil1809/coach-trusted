from rest_framework import serializers

from coach.models import CoachMedia


class CoachMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachMedia
        fields = [
            "id",
            "file",
            "created_at",
        ]
