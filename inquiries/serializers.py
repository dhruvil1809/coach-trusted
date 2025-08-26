from rest_framework import serializers

from inquiries.models import GeneralInquiry


class GeneralInquirySerializer(serializers.ModelSerializer):
    """Serializer for creating and retrieving GeneralInquiry objects."""

    class Meta:
        model = GeneralInquiry
        fields = [
            "id",
            "subject",
            "message",
            "business_name",
            "first_name",
            "last_name",
            "email",
            "country",
            "phone",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "subject": {"required": True},
            "message": {"required": True},
            "business_name": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "country": {"required": True},
            "phone": {"required": True},
        }

    def validate_email(self, value):
        """Validate email format."""
        if not value:
            msg = "Email is required."
            raise serializers.ValidationError(msg)
        return value

    def validate_subject(self, value):
        """Validate subject is not empty."""
        if not value or not value.strip():
            msg = "Subject is required and cannot be empty."
            raise serializers.ValidationError(
                msg,
            )
        return value

    def validate_message(self, value):
        """Validate message is not empty."""
        if not value or not value.strip():
            msg = "Message is required and cannot be empty."
            raise serializers.ValidationError(
                msg,
            )
        return value

    def validate_business_name(self, value):
        """Validate business_name is not empty."""
        if not value or not value.strip():
            msg = "Business name is required and cannot be empty."
            raise serializers.ValidationError(
                msg,
            )
        return value

    def validate_first_name(self, value):
        """Validate first_name is not empty."""
        if not value or not value.strip():
            msg = "First name is required and cannot be empty."
            raise serializers.ValidationError(
                msg,
            )
        return value

    def validate_last_name(self, value):
        """Validate last_name is not empty."""
        if not value or not value.strip():
            msg = "Last name is required and cannot be empty."
            raise serializers.ValidationError(
                msg,
            )
        return value

    def validate_country(self, value):
        """Validate country is not empty."""
        if not value or not value.strip():
            msg = "Country is required and cannot be empty."
            raise serializers.ValidationError(
                msg,
            )
        return value
