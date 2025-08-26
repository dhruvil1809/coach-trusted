from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView

from .models import MetaContent
from .serializers import MetaContentDetailSerializer
from .serializers import MetaContentListSerializer


class MetaContentListView(ListAPIView):
    """
    API view to list all MetaContent instances.
    """

    permission_classes = []
    queryset = MetaContent.objects.all()
    serializer_class = MetaContentListSerializer


class MetaContentDetailView(RetrieveAPIView):
    """
    API view to retrieve a specific MetaContent instance by ID.
    """

    permission_classes = []
    queryset = MetaContent.objects.all()
    serializer_class = MetaContentDetailSerializer
