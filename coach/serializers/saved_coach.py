from rest_framework import serializers

from coach.models import Coach
from coach.models import SavedCoach

from .coach import CoachDetailSerializer


class SavedCoachSerializer(serializers.ModelSerializer):
    """
    Serializer for the SavedCoach model.
    """

    coach = CoachDetailSerializer(read_only=True)

    class Meta:
        model = SavedCoach
        fields = ["uuid", "coach", "created_at"]
        read_only_fields = ["uuid", "created_at"]


class CreateSavedCoachSerializer(serializers.Serializer):
    """
    Serializer for creating a saved coach.
    """

    coach_uuid = serializers.UUIDField(write_only=True)

    def validate_coach_uuid(self, value):
        coach = Coach.objects.filter(
            uuid=value,
            review_status=Coach.REVIEW_APPROVED,
        ).first()
        if not coach:
            msg = "Coach with this UUID does not exist or is not available."
            raise serializers.ValidationError(msg)
        return value
