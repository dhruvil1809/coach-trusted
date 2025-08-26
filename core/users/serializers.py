from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Profile
from .models import User


class ProfileSerializer(ModelSerializer):
    coach_uuid = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "profile_picture",
            "coach_uuid",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "phone_number": {"required": True},
        }

    def validate_first_name(self, value):
        if not value:
            msg = "First name is required."
            raise serializers.ValidationError(msg)
        return value

    def validate_last_name(self, value):
        if not value:
            msg = "Last name is required."
            raise serializers.ValidationError(msg)
        return value

    def validate_email(self, value):
        if not value:
            msg = "Email is required."
            raise serializers.ValidationError(msg)

        if Profile.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            msg = "Email already used by another user."
            raise serializers.ValidationError(msg)

        return value

    def get_coach_uuid(self, obj):
        if hasattr(obj, "user") and hasattr(obj.user, "coach") and obj.user.coach:
            return obj.user.coach.uuid

        return None


class UserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
        ]
        read_only_fields = ["id"]


class ProfileListSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "profile_picture",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserListWithProfileSerializer(ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "profile",
        ]
        read_only_fields = ["id"]


class ProfileListWithUserSerializer(ModelSerializer):
    user = UserListSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "profile_picture",
            "created_at",
            "updated_at",
            "user",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
