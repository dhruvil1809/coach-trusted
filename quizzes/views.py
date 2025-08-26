# Create your views here.
from drf_spectacular.utils import extend_schema
from rest_framework import filters
from rest_framework import generics
from rest_framework import permissions

from .models import Fields
from .models import Quiz
from .serializers import FieldsSerializer
from .serializers import QuizCreateSerializer


@extend_schema(
    summary="List all quiz fields",
    description="Returns a list of all quiz fields, supports ordering by id and name. No pagination.",  # noqa: E501
    responses={200: FieldsSerializer(many=True)},
)
class FieldsListView(generics.ListAPIView):
    queryset = Fields.objects.all()
    serializer_class = FieldsSerializer
    permission_classes = []
    pagination_class = None
    filter_backends = [filters.OrderingFilter]
    ordering_fields = [
        "id",
        "name",
    ]
    ordering = ["name"]


@extend_schema(
    summary="Create a new quiz entry",
    description="Creates a new quiz entry with the provided data.",
    request=QuizCreateSerializer,
    responses={201: QuizCreateSerializer},
)
class QuizCreateView(generics.CreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizCreateSerializer
    permission_classes = [permissions.AllowAny]
