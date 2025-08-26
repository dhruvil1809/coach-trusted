from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from inquiries.models import GeneralInquiry
from inquiries.serializers import GeneralInquirySerializer


class CreateGeneralInquiryView(CreateAPIView):
    """
    Create a new general inquiry without authentication.

    This endpoint allows anonymous users to submit general inquiries
    about the platform or business-related questions.
    """

    queryset = GeneralInquiry.objects.all()
    serializer_class = GeneralInquirySerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Create General Inquiry",
        description="Submit a general inquiry without requiring authentication. "
        "This endpoint is used for contact forms and general business inquiries.",
        responses={
            201: GeneralInquirySerializer,
            400: "Bad Request - Validation errors",
        },
    )
    def post(self, request, *args, **kwargs):
        """Create a new general inquiry."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
