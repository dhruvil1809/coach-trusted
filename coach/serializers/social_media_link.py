from rest_framework import serializers

from coach.models import SocialMediaLink


class SocialMediaLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for the SocialMediaLink model.
    """

    class Meta:
        model = SocialMediaLink
        fields = [
            "uuid",
            "instagram",
            "facebook",
            "linkedin",
            "youtube",
            "tiktok",
            "x",
            "trustpilot",
            "google",
            "provexpert",
        ]
        read_only_fields = ["uuid"]
