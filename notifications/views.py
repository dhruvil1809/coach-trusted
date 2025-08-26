from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.paginations import NotificationPagination
from notifications.serializers import NotificationListSerializer
from notifications.serializers import NotificationUpdateSerializer

from .models import Notification


@extend_schema(
    summary="List User Notifications",
    description="Get a paginated list of unread and non-deleted notifications for the authenticated user, ordered by creation date (newest first).",  # noqa: E501
    responses={
        200: OpenApiResponse(
            description="List of notifications",
            response=NotificationListSerializer,
        ),
        401: OpenApiResponse(
            description="Authentication required",
        ),
    },
)
class NotificationListView(ListAPIView):
    serializer_class = NotificationListSerializer
    pagination_class = NotificationPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = [
        "created_at",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(
            to=user,
            is_read=False,
            is_deleted=False,
        ).order_by("-created_at")


@extend_schema(
    summary="Update Notification Status",
    description="Update notification status to mark as read or deleted. "
    "Only the notification recipient can update their notifications.",
    request=NotificationUpdateSerializer,
    responses={
        200: OpenApiResponse(
            description="Notification updated successfully",
            response=NotificationListSerializer,
        ),
        400: OpenApiResponse(
            description="Bad request - invalid data",
        ),
        401: OpenApiResponse(
            description="Authentication required",
        ),
        403: OpenApiResponse(
            description="Permission denied - not the notification recipient",
        ),
        404: OpenApiResponse(
            description="Notification not found",
        ),
    },
)
class NotificationUpdateView(UpdateAPIView):
    serializer_class = NotificationUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        """Only allow users to update their own notifications"""
        return Notification.objects.filter(to=self.request.user, is_deleted=False)

    def update(self, request, *args, **kwargs):
        """Update notification and return the updated notification data"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return the updated notification using the list serializer
        response_serializer = NotificationListSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
