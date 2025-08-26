from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authentication import firebase
from authentication.serializers import LoginSerializer
from authentication.serializers import LoginWithGoogleSerializer
from authentication.serializers import PasswordResetConfirmSerializer
from authentication.serializers import PasswordResetRequestSerializer
from authentication.serializers import RefreshTokenSerializer
from authentication.serializers import RegisterConfirmationSerializer
from authentication.serializers import RegisterSerializer
from authentication.serializers import ResendVerificationCodeSerializer
from core.users.models import Profile
from core.users.models import User


class RefreshTokenView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = RefreshTokenSerializer

    @extend_schema(
        summary="Refresh JWT token",
        description="Refreshes the JWT token using the refresh token.",
        responses={
            200: OpenApiResponse(
                description="New JWT tokens",
            ),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data.get("refresh")
        try:
            token = RefreshToken(refresh)
        except Exception:  # noqa: BLE001
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "refresh": str(token),
                "access": str(token.access_token),
            },
        )


class ValidateTokenView(APIView):
    @extend_schema(
        summary="Validate JWT token",
        description="Validates the JWT token and returns user information.",
        responses={
            200: OpenApiResponse(),
        },
    )
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                "detail": "Token is valid",
            },
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    serializer_class = LoginSerializer
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Login user",
        description="Authenticates a user using email and password and returns JWT tokens.",  # noqa: E501
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description="User JWT tokens",
                examples={
                    "application/json": {
                        "refresh": "string",
                        "access": "string",
                    },
                },
            ),
            400: OpenApiResponse(
                description="Invalid credentials or account not activated",
                examples={
                    "application/json": {"error": "Invalid password"},
                },
            ),
            403: OpenApiResponse(
                description="Account not activated",
                examples={
                    "application/json": {
                        "error": "Account not activated. Please check your email for the verification code.",  # noqa: E501
                    },
                },
            ),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        # First, check if user exists (regardless of active status)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if password is correct
        if not user.check_password(password):
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user account is active
        if not user.is_active:
            return Response(
                {
                    "error": "Account not activated. Please check your email for the verification code.",  # noqa: E501
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        )


class RegisterView(APIView):
    serializer_class = RegisterSerializer
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Register a new user",
        description="Registers a new user and sends a verification code to their email.",  # noqa: E501
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description="Verification code sent to email",
                examples={
                    "application/json": {"detail": "Verification code sent to email"},
                },
            ),
            400: OpenApiResponse(
                description="Validation error",
                examples={
                    "application/json": {
                        "email": ["This field is required."],
                        "password": ["This field must be at least 8 characters long."],
                    },
                },
            ),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = User.objects.create_user(
                username=f"{serializer.validated_data.get('email')}_{get_random_string(5)}",
                first_name=serializer.validated_data.get("first_name"),
                last_name=serializer.validated_data.get("last_name"),
                email=serializer.validated_data.get("email"),
                phone_number=serializer.validated_data.get("phone_number"),
                password=serializer.validated_data.get("password"),
            )
            user.is_active = False
            user.save()

            # Create a profile for the user
            Profile.objects.create(
                user=user,
                first_name=serializer.validated_data.get("first_name"),
                last_name=serializer.validated_data.get("last_name"),
                email=serializer.validated_data.get("email"),
                country_code=serializer.validated_data.get("country_code"),
                phone_number=serializer.validated_data.get("phone_number"),
            )
            user.send_verification_code()

        return Response(
            {"detail": "Verification code sent to email"},
            status=status.HTTP_201_CREATED,
        )


class RegisterConfirmationView(APIView):
    serializer_class = RegisterConfirmationSerializer
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Confirm registration",
        description="Confirms the registration of a new user using a verification code.",  # noqa: E501
        request=RegisterConfirmationSerializer,
        responses={
            200: OpenApiResponse(
                description="User JWT tokens",
            ),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")

        user = User.objects.filter(email=email).first()
        user.is_active = True
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class LoginWithGoogleView(APIView):
    serializer_class = LoginWithGoogleSerializer
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Login with Google",
        description="Login a user using Google authentication.",
        request=LoginWithGoogleSerializer,
        responses={
            200: OpenApiResponse(
                description="User JWT tokens",
            ),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data.get("token")
        user_info = firebase.get_user_info(token)

        user, _ = User.objects.get_or_create(
            email=user_info.get("email"),
            defaults={
                "username": f"{user_info.get('email')}_{get_random_string(5)}",
                "first_name": user_info.get("first_name"),
                "last_name": user_info.get("last_name"),
                # "photo_url": user_info["photo_url"],  # noqa: ERA001
            },
        )

        # Activate the user if they are not already active
        if not user.is_active:
            user.is_active = True
            user.save()

        # Create a profile for the user if it doesn't exist
        if not hasattr(user, "profile"):
            Profile.objects.create(
                user=user,
                first_name=user_info.get("first_name"),
                last_name=user_info.get("last_name"),
                email=user_info.get("email"),
                # phone_number=user_info.get("phone_number"),  # noqa: ERA001
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class ResendVerificationCodeView(APIView):
    serializer_class = ResendVerificationCodeSerializer
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Resend verification code",
        description="Resends a new verification code to the user's email address.",
        request=ResendVerificationCodeSerializer,
        responses={
            200: OpenApiResponse(
                description="Verification code sent",
                examples={
                    "application/json": {"detail": "Verification code sent to email"},
                },
            ),
            400: OpenApiResponse(
                description="Validation error",
                examples={
                    "application/json": {
                        "email": ["User not found"],
                    },
                },
            ),
            429: OpenApiResponse(
                description="Rate limit exceeded",
                examples={
                    "application/json": {
                        "error": "Please wait before requesting another verification code",  # noqa: E501
                    },
                },
            ),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        user = User.objects.filter(email__iexact=email).first()

        # Check if user has recently requested a verification code (rate limiting)
        recent_code = user.verification_codes.filter(
            created_at__gte=timezone.now() - timezone.timedelta(minutes=1),
        ).first()

        if recent_code:
            return Response(
                {"error": "Please wait before requesting another verification code"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Send new verification code (this will invalidate old codes)
        user.send_verification_code()

        return Response(
            {"detail": "Verification code sent to email"},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    serializer_class = PasswordResetRequestSerializer
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Request password reset",
        description="Sends a password reset email to the user's email address.",
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="Password reset email sent",
                examples={
                    "application/json": {"detail": "Password reset email sent"},
                },
            ),
            400: OpenApiResponse(
                description="Validation error",
                examples={
                    "application/json": {
                        "email": ["User not found"],
                    },
                },
            ),
            429: OpenApiResponse(
                description="Rate limit exceeded",
                examples={
                    "application/json": {
                        "error": "Please wait before requesting another password reset",
                    },
                },
            ),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        user = User.objects.filter(email__iexact=email).first()

        # Check if user has recently requested a password reset (rate limiting)
        recent_reset = user.password_reset_tokens.filter(
            created_at__gte=timezone.now() - timezone.timedelta(minutes=5),
        ).first()

        if recent_reset:
            return Response(
                {"error": "Please wait before requesting another password reset"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Generate password reset token
        reset_token = get_random_string(32)
        user.password_reset_tokens.create(token=reset_token)

        # Send password reset email
        user.send_password_reset_email(reset_token)

        return Response(
            {"detail": "Password reset email sent",
             "token": reset_token},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    serializer_class = PasswordResetConfirmSerializer
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Confirm password reset",
        description="Confirms the password reset using the token from the email.",
        request=PasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(
                description="Password reset successful",
                examples={
                    "application/json": {"detail": "Password reset successful"},
                },
            ),
            400: OpenApiResponse(
                description="Validation error",
                examples={
                    "application/json": {
                        "token": ["Invalid or expired token"],
                        "new_password": ["This field must be at least 8 characters long."],
                    },
                },
            ),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data.get("token")
        new_password = serializer.validated_data.get("new_password")

        # Find the password reset token
        reset_token = User.objects.filter(
            password_reset_tokens__token=token,
            password_reset_tokens__created_at__gte=timezone.now() - timezone.timedelta(hours=24),
        ).first()

        if not reset_token:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update user password
        reset_token.set_password(new_password)
        reset_token.save()

        # Delete all password reset tokens for this user
        reset_token.password_reset_tokens.all().delete()

        return Response(
            {"detail": "Password reset successful"},
            status=status.HTTP_200_OK,
        )
