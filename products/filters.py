import django_filters
from django_filters import rest_framework as filters

from .models import Product


class ProductFilter(filters.FilterSet):
    """
    Custom filter set for Product model with advanced price filtering.
    """

    # Price filters
    price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="exact",
        help_text="Filter by exact price",
    )
    price__gte = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        help_text="Filter by price greater than or equal to this value",
    )
    price__lte = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        help_text="Filter by price less than or equal to this value",
    )

    class Meta:
        model = Product
        fields = [
            "category__id",
            "category__slug",
            "category__name",
            "product_type__id",
            "product_type__name",
            "language",
            "coach__id",
            "coach__first_name",
            "coach__last_name",
            "is_featured",
            "price",
            "price__gte",
            "price__lte",
        ]
