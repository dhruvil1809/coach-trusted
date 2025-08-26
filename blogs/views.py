from django.db.models import Count
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from .filters import PostFilter
from .models import Category
from .models import Post
from .paginations import PostPagination
from .serializers import CategoryListSerializer
from .serializers import PostDetailSerializer
from .serializers import PostListSerializer


class CategoryListAPIView(ListAPIView):
    """
    API view to retrieve a list of all blog categories without pagination.
    """

    serializer_class = CategoryListSerializer
    permission_classes = [AllowAny]
    pagination_class = None  # Disable pagination
    filter_backends = [OrderingFilter]
    ordering_fields = [
        "name",
        "slug",
        "post_count",
    ]
    ordering = ["name"]

    def get_queryset(self):
        """Return all categories with post count annotation."""
        return Category.objects.annotate(
            post_count=Count("posts", filter=Q(posts__status=Post.STATUS_PUBLISHED)),
        ).order_by("name")


class PostListAPIView(ListAPIView):
    """
    API view to retrieve a list of published blog posts.
    Supports filtering by category name and category slug.
    """

    serializer_class = PostListSerializer
    permission_classes = [AllowAny]
    pagination_class = PostPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = PostFilter
    search_fields = [
        "title",
        "content",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "title",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return only published posts, ordered by creation date (newest first)."""
        return Post.objects.filter(status=Post.STATUS_PUBLISHED).order_by("-created_at")


class PostDetailAPIView(RetrieveAPIView):
    """
    API view to retrieve a single blog post by slug.
    """

    serializer_class = PostDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        """Return only published posts."""
        return Post.objects.filter(status=Post.STATUS_PUBLISHED)


# Create your views here.
