from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import ProfileSerializer


class RetrieveUpdateProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Returns the current user's profile.
        """

        return (
            self.request.user.profile if hasattr(self.request.user, "profile") else None
        )

    @extend_schema(
        summary="Get user profile",
        description="Retrieve the authenticated user's profile information.",
        responses={
            200: ProfileSerializer,
            403: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        if not profile:
            return Response(
                {"detail": "There is no profile for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update user profile",
        description="Update the authenticated user's profile information.",
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: OpenApiResponse(description="Bad request, validation error."),
            403: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update user profile",
        description="Partially update the authenticated user's profile information.",
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: OpenApiResponse(description="Bad request, validation error."),
            403: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Update user profile",
        description="Update the authenticated user's profile information using POST method.",  # noqa: E501
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: OpenApiResponse(description="Bad request, validation error."),
            403: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
