from rest_framework import serializers

from coach.models import Coach
from coach.models import CoachReview


class CoachReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a coach review.
    """

    coach_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = CoachReview
        fields = [
            "coach_uuid",
            "rating",
            "comment",
            "date",
            "first_name",
            "last_name",
            "email",
            "proof_file",
        ]

    def validate_coach_uuid(self, value):
        """
        Validate that the coach with the given UUID exists and is approved
        """
        coach = Coach.objects.filter(
            uuid=value,
            review_status=Coach.REVIEW_APPROVED,
        ).first()
        if not coach:
            msg = "Coach with this UUID does not exist or is not available for reviews."
            raise serializers.ValidationError(msg)
        return value

    def create(self, validated_data):
        coach_uuid = validated_data.pop("coach_uuid")
        coach = Coach.objects.get(
            uuid=coach_uuid,
            review_status=Coach.REVIEW_APPROVED,
        )

        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None

        return CoachReview.objects.create(
            coach=coach,
            user=user,
            status=CoachReview.STATUS_PENDING,
            **validated_data,
        )


class CoachReviewListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing coach reviews.
    """

    class Meta:
        model = CoachReview
        fields = [
            "uuid",
            "rating",
            "comment",
            "date",
            "first_name",
            "last_name",
            "created_at",
        ]
        read_only_fields = fields
