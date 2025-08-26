from rest_framework import serializers

from .models import MetaContent


class MetaContentListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing MetaContent instances.
    """

    class Meta:
        model = MetaContent
        fields = "__all__"


class MetaContentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed view of MetaContent instances.
    """

    class Meta:
        model = MetaContent
        fields = "__all__"
