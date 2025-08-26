from django_filters import rest_framework as filters

from .models import Post


class PostFilter(filters.FilterSet):
    """
    Filter set for Post model to enable filtering by category name and slug.
    """

    category_name = filters.CharFilter(
        field_name="category__name",
        lookup_expr="iexact",
        help_text="Filter posts by category name (case-insensitive exact match)",
    )

    category_slug = filters.CharFilter(
        field_name="category__slug",
        lookup_expr="exact",
        help_text="Filter posts by category slug (exact match)",
    )

    class Meta:
        model = Post
        fields = ["category_name", "category_slug"]
