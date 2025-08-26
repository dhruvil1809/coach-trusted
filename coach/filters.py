from django.db.models import Q
from django_filters import rest_framework as filters

from coach.models import Coach


class CoachFilter(filters.FilterSet):
    """
    CoachFilter is a Django FilterSet class used to filter Coach objects based on
    various criteria.

    Filters:
        - category: Filters coaches by category ID or category name
          (supports multiple values)
        - subcategory: Filters coaches by subcategory ID or subcategory name
          (supports multiple values)
        - type: Filters coaches by type (online/offline)
        - verification_status: Filters coaches by verification status
        - experience_level: Filters coaches by experience level
        - location: Filters coaches by location (exact or contains)
        - avg_rating: Filters coaches by exact average rating
        - avg_rating_min: Filters coaches by minimum average rating
        - avg_rating_max: Filters coaches by maximum average rating
        - is_claimable: Filters coaches by whether they can be claimed (true/false)

    Examples:
        - Filter by multiple categories: ?category=1&category=2 or ?category=1,2
        - Filter by multiple subcategories: ?subcategory=1&subcategory=2 or
          ?subcategory=1,2
        - Filter by category names:
          ?category__name__in=Life Coaching,Business Coaching
        - Filter by minimum rating: ?avg_rating_min=4.0
        - Filter by rating range: ?avg_rating_min=3.5&avg_rating_max=5.0
        - Filter by claimable coaches: ?is_claimable=true
        - Filter by non-claimable coaches: ?is_claimable=false
    """

    # Multiple category filters - handle both IDs and names
    category = filters.CharFilter(method="filter_categories")
    category__name__in = filters.CharFilter(
        field_name="category__name",
        lookup_expr="in",
        method="filter_category_names",
    )

    # Multiple subcategory filters - handle both IDs and names
    subcategory = filters.CharFilter(method="filter_subcategories")
    subcategory__name__in = filters.CharFilter(
        field_name="subcategory__name",
        lookup_expr="in",
        method="filter_subcategory_names",
    )

    # Filter by whether coach is claimable (has no associated user)
    is_claimable = filters.BooleanFilter(
        method="filter_is_claimable",
        label="Is Claimable",
    )

    # Average rating filters
    avg_rating = filters.NumberFilter(
        field_name="avg_rating",
        lookup_expr="exact",
        label="Average Rating",
    )
    avg_rating_min = filters.NumberFilter(
        field_name="avg_rating",
        lookup_expr="gte",
        label="Minimum Average Rating",
    )
    avg_rating_max = filters.NumberFilter(
        field_name="avg_rating",
        lookup_expr="lte",
        label="Maximum Average Rating",
    )
    rating = filters.NumberFilter(
        field_name="avg_rating",
        lookup_expr="gte",
        label="Rating (Will have same effect as avg_rating_min)",
    )

    def filter_categories(self, queryset, name, value):
        """
        Filter by category IDs, names, or string representations
        Handles values like: "1", "category_9", "Life Coaching", "1,2", etc.
        """
        if not value:
            return queryset

        # Handle multiple values (comma-separated)
        if isinstance(value, str):
            values = [v.strip() for v in value.split(",") if v.strip()]
        else:
            values = [str(value)]

        category_ids = []
        category_names = []

        for val in values:
            # Check if it's a numeric ID
            if val.isdigit():
                category_ids.append(int(val))
            # Check if it's in format "category_X"
            elif val.startswith("category_") and val[9:].isdigit():
                category_ids.append(int(val[9:]))
            else:
                # Treat as category name
                category_names.append(val)

        # Build filter conditions
        filters_q = None
        if category_ids:
            filters_q = Q(category__id__in=category_ids)

        if category_names:
            name_filter = Q(category__name__in=category_names)
            filters_q = filters_q | name_filter if filters_q else name_filter

        if filters_q:
            return queryset.filter(filters_q)
        return queryset

    def filter_subcategories(self, queryset, name, value):
        """
        Filter by subcategory IDs, names, or string representations
        Handles values like: "1", "subcategory_9", "Business Development", "1,2", etc.
        """
        if not value:
            return queryset

        # Handle multiple values (comma-separated)
        if isinstance(value, str):
            values = [v.strip() for v in value.split(",") if v.strip()]
        else:
            values = [str(value)]

        subcategory_ids = []
        subcategory_names = []

        for val in values:
            # Check if it's a numeric ID
            if val.isdigit():
                subcategory_ids.append(int(val))
            # Check if it's in format "subcategory_X"
            elif val.startswith("subcategory_") and val[12:].isdigit():
                subcategory_ids.append(int(val[12:]))
            else:
                # Treat as subcategory name
                subcategory_names.append(val)

        # Build filter conditions
        filters_q = None
        if subcategory_ids:
            filters_q = Q(subcategory__id__in=subcategory_ids)

        if subcategory_names:
            name_filter = Q(subcategory__name__in=subcategory_names)
            filters_q = filters_q | name_filter if filters_q else name_filter

        if filters_q:
            return queryset.filter(filters_q)
        return queryset

    def filter_category_names(self, queryset, name, value):
        """
        Filter by multiple category names separated by comma
        """
        if not value:
            return queryset

        # Split comma-separated values and strip whitespace
        category_names = [name.strip() for name in value.split(",") if name.strip()]
        if category_names:
            return queryset.filter(category__name__in=category_names)
        return queryset

    def filter_subcategory_names(self, queryset, name, value):
        """
        Filter by multiple subcategory names separated by comma
        """
        if not value:
            return queryset

        # Split comma-separated values and strip whitespace
        subcategory_names = [name.strip() for name in value.split(",") if name.strip()]
        if subcategory_names:
            return queryset.filter(subcategory__name__in=subcategory_names)
        return queryset

    def filter_is_claimable(self, queryset, name, value):
        """
        Filter coaches based on whether they are claimable or not.
        A coach is claimable if it has no associated user (user=None).
        """
        if value is True:
            return queryset.filter(user__isnull=True)
        if value is False:
            return queryset.filter(user__isnull=False)
        return queryset

    class Meta:
        model = Coach
        fields = {
            "type": ["exact"],
            "verification_status": ["exact"],
            "experience_level": ["exact"],
            "location": ["exact", "icontains"],
            "category": ["exact"],
            "category__name": ["exact", "icontains"],
            "subcategory": ["exact"],
            "subcategory__name": ["exact", "icontains"],
        }
