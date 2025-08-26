from rest_framework import serializers

from coach.models import ClaimCoachRequest
from coach.models import Coach


class ClaimCoachRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for claiming a coach profile.
    """

    coach_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = ClaimCoachRequest
        fields = [
            "coach_uuid",
            "first_name",
            "last_name",
            "email",
            "country",
            "phone_number",
        ]

    def validate_coach_uuid(self, value):
        """
        Validate that:
        1. The coach with the given UUID exists
        2. The coach is not already claimed
        """
        coach = Coach.objects.filter(uuid=value).first()
        if not coach:
            msg = "Coach with this UUID does not exist."
            raise serializers.ValidationError(msg)

        if coach.user is not None:
            msg = "This coach profile is already claimed."
            raise serializers.ValidationError(msg)

        # Removed validation for duplicate pending claim requests to allow multiple requests  # noqa: E501
        # as the approval will be handled in the admin panel

        return value

    def validate(self, data):
        """
        Validate that the user doesn't already have a coach profile.
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            user = request.user

            # Check if user already has a coach profile
            if hasattr(user, "coach") and user.coach:
                msg = "You already have a coach profile."
                raise serializers.ValidationError(msg)

            # Removed validation for user's pending claim requests to allow multiple requests  # noqa: E501

        return data

    def create(self, validated_data):
        coach_uuid = validated_data.pop("coach_uuid")
        coach = Coach.objects.get(uuid=coach_uuid)

        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None

        return ClaimCoachRequest.objects.create(
            coach=coach,
            user=user,
            **validated_data,
        )
