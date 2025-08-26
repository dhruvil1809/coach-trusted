from rest_framework import serializers

from authentication import firebase
from core.users.models import User


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    country_code = serializers.CharField(max_length=5)
    phone_number = serializers.CharField()
    password = serializers.CharField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            msg = "Email already exists"
            raise serializers.ValidationError(msg)
        return value

    def validate_password(self, value):
        if len(value) < 8:  # noqa: PLR2004
            msg = "Password must be at least 8 characters long"
            raise serializers.ValidationError(msg)
        return value

    # Validate phone number to ensure it is unique
    # and not already in use by another user
    # def validate_phone_number(self, value):
    #     if User.objects.filter(phone_number=value).exists():
    #         msg = "Phone number already exists"  # noqa: ERA001
    #         raise serializers.ValidationError(msg)  # noqa: ERA001
    #     return value  # noqa: ERA001


class RegisterConfirmationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

    def validate(self, attrs):
        user = User.objects.filter(email=attrs.get("email")).first()

        if not user:
            msg = "User not found"
            raise serializers.ValidationError(msg)

        if user.is_active:
            msg = "User already registered"
            raise serializers.ValidationError(msg)

        verification_code = user.verification_codes.last()
        if not verification_code or verification_code.code != attrs.get(
            "code",
        ):
            msg = "Invalid verification code"
            raise serializers.ValidationError(msg)

        return attrs


class LoginWithGoogleSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            firebase.validate_token(value)
        except Exception as e:
            msg = "Invalid token"
            raise serializers.ValidationError(msg) from e

        return value


class ResendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email__iexact=value).first()

        if not user:
            msg = "User not found"
            raise serializers.ValidationError(msg)

        if user.is_active:
            msg = "User account is already active"
            raise serializers.ValidationError(msg)

        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email__iexact=value).first()

        if not user:
            msg = "User not found"
            raise serializers.ValidationError(msg)

        if not user.is_active:
            msg = "User account is not active"
            raise serializers.ValidationError(msg)

        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        if len(value) < 8:  # noqa: PLR2004
            msg = "Password must be at least 8 characters long"
            raise serializers.ValidationError(msg)
        return value
