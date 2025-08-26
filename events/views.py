from django.db.models import Avg
from django.db.models import Case
from django.db.models import Count
from django.db.models import Prefetch
from django.db.models import Q
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Coalesce
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from coach.models import Coach
from coach.models import CoachReview

from .models import Event
from .models import SavedEvent
from .serializers import AddSavedEventSerializer
from .serializers import EventDetailSerializer
from .serializers import EventListSerializer
from .serializers import SavedEventListSerializer


class EventFilter(filters.FilterSet):
    """
    EventFilter is a Django FilterSet class used to filter Event objects based on various criteria.
    Filters:
        - min_price: Filters events where the ticket price is greater than or equal to the specified value.
        - max_price: Filters events where the ticket price is less than or equal to the specified value.
        - coach_category: Filters events by coach category ID or category name (supports multiple values)
        - coach_subcategory: Filters events by coach subcategory ID or subcategory name (supports multiple values)
    Meta:
        - model: The model being filtered is `Event`.
        - fields:
            - type: Filters events based on their type (online or offline). Supports exact lookup.
            - location: Filters events based on their location. Supports exact and contains lookups.
            - start_datetime: Filters events based on their start date and time. Supports exact, greater than or equal to (gte), and less than or equal to (lte) lookups.
            - end_datetime: Filters events based on their end date and time. Supports exact, greater than or equal to (gte), and less than or equal to (lte) lookups.
            - coach: Filters events based on the coach ID. Supports exact lookup.
            - coach__uuid: Filters events based on the coach UUID. Supports exact lookup.
            - coach__verification_status: Filters events based on the verification status of the associated coach. Supports exact lookup.
            - coach__experience_level: Filters events based on the experience level of the associated coach. Supports exact lookup.
            - coach__category: Filters events based on the coach's category ID. Supports exact lookup.
            - coach__category__name: Filters events based on the coach's category name. Supports exact and contains lookups.
            - coach__subcategory: Filters events based on the coach's subcategory ID. Supports exact lookup.
            - coach__subcategory__name: Filters events based on the coach's subcategory name. Supports exact and contains lookups.
    """  # noqa: E501

    min_price = filters.NumberFilter(field_name="tickets__price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="tickets__price", lookup_expr="lte")

    # Coach category filters - handle both IDs and names
    coach_category = filters.CharFilter(method="filter_coach_categories")
    coach_category__name__in = filters.CharFilter(
        field_name="coach__category__name",
        lookup_expr="in",
        method="filter_coach_category_names",
    )

    # Coach subcategory filters - handle both IDs and names
    coach_subcategory = filters.CharFilter(method="filter_coach_subcategories")
    coach_subcategory__name__in = filters.CharFilter(
        field_name="coach__subcategory__name",
        lookup_expr="in",
        method="filter_coach_subcategory_names",
    )

    def filter_coach_categories(self, queryset, name, value):
        """
        Filter by coach category IDs, names, or string representations
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
            filters_q = Q(coach__category__id__in=category_ids)

        if category_names:
            name_filter = Q(coach__category__name__in=category_names)
            filters_q = filters_q | name_filter if filters_q else name_filter

        if filters_q:
            return queryset.filter(filters_q)
        return queryset

    def filter_coach_subcategories(self, queryset, name, value):
        """
        Filter by coach subcategory IDs, names, or string representations
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
            filters_q = Q(coach__subcategory__id__in=subcategory_ids)

        if subcategory_names:
            name_filter = Q(coach__subcategory__name__in=subcategory_names)
            filters_q = filters_q | name_filter if filters_q else name_filter

        if filters_q:
            return queryset.filter(filters_q)
        return queryset

    def filter_coach_category_names(self, queryset, name, value):
        """
        Filter by multiple coach category names separated by comma
        """
        if not value:
            return queryset

        # Split comma-separated values and strip whitespace
        category_names = [name.strip() for name in value.split(",") if name.strip()]
        if category_names:
            return queryset.filter(coach__category__name__in=category_names)
        return queryset

    def filter_coach_subcategory_names(self, queryset, name, value):
        """
        Filter by multiple coach subcategory names separated by comma
        """
        if not value:
            return queryset

        # Split comma-separated values and strip whitespace
        subcategory_names = [name.strip() for name in value.split(",") if name.strip()]
        if subcategory_names:
            return queryset.filter(coach__subcategory__name__in=subcategory_names)
        return queryset

    class Meta:
        model = Event
        fields = {
            "type": ["exact"],
            "location": ["exact", "contains"],
            "start_datetime": ["exact", "gte", "lte"],
            "end_datetime": ["exact", "gte", "lte"],
            "coach": ["exact"],
            "coach__uuid": ["exact"],
            "coach__verification_status": ["exact"],
            "coach__experience_level": ["exact"],
            "coach__category": ["exact"],
            "coach__category__name": ["exact", "icontains"],
            "coach__subcategory": ["exact"],
            "coach__subcategory__name": ["exact", "icontains"],
            "is_featured": ["exact"],
        }


class CustomPagination(PageNumberPagination):
    """
    CustomPagination is a pagination class that extends PageNumberPagination to provide
    customizable pagination behavior for API views.
    Attributes:
        page_size (int): The default number of items to display per page. Defaults to 10.
        page_size_query_param (str): The query parameter name that allows clients to set
            the number of items per page. Defaults to "page_size".
        max_page_size (int): The maximum number of items allowed per page. Defaults to 100.
    """  # noqa: E501

    page_size = 10  # Default page size
    page_size_query_param = "page_size"
    max_page_size = 100  # Maximum page size


@extend_schema(
    summary="List Events",
    description="Get a paginated list of all events with filtering, searching, and ordering capabilities.",  # noqa: E501
    responses={
        200: OpenApiResponse(
            description="List of events",
            response=EventListSerializer,
        ),
    },
)
class EventListAPIView(ListAPIView):
    """
    EventListAPIView is a view that provides a paginated list of events with filtering,
    searching, and ordering capabilities.
    """

    permission_classes = []
    queryset = (
        Event.objects.all()
        .prefetch_related(
            "tickets",
            Prefetch(
                "coach",
                queryset=Coach.objects.annotate(
                    avg_rating=Coalesce(
                        Avg(
                            Case(
                                When(
                                    reviews__status=CoachReview.STATUS_APPROVED,
                                    then="reviews__rating",
                                ),
                            ),
                        ),
                        Value(0.0),
                    ),
                    review_count=Count(
                        Case(
                            When(
                                reviews__status=CoachReview.STATUS_APPROVED,
                                then=1,
                            ),
                        ),
                    ),
                )
                .select_related("user", "category")
                .prefetch_related("subcategory"),
            ),
        )
        .order_by("start_datetime", "end_datetime", "-created_at")
    )
    serializer_class = EventListSerializer
    pagination_class = CustomPagination
    filterset_class = EventFilter
    filter_backends = [
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        "name",
        "description",
        "location",
        "coach__first_name",
        "coach__last_name",
        "coach__category__name",
        "coach__subcategory__name",
    ]
    ordering_fields = [
        "name",
        "type",
        "created_at",
        "updated_at",
        "start_datetime",
        "end_datetime",
        "coach__first_name",
        "coach__last_name",
        "coach__category__name",
        "coach__subcategory__name",
        "coach__verification_status",
        "coach__experience_level",
    ]


@extend_schema(
    summary="Retrieve Event",
    description="Get detailed information about a specific event by its slug.",
    responses={
        200: OpenApiResponse(
            description="Event details",
            response=EventDetailSerializer,
        ),
        404: OpenApiResponse(description="Event not found"),
    },
)
class EventRetrieveAPIView(RetrieveAPIView):
    """
    EventRetrieveAPIView is a view that provides detailed information about a specific event.
    """  # noqa: E501

    permission_classes = []
    queryset = Event.objects.all().prefetch_related(
        "tickets",
        "media",
        Prefetch(
            "coach",
            queryset=Coach.objects.annotate(
                avg_rating=Coalesce(
                    Avg(
                        Case(
                            When(
                                reviews__status=CoachReview.STATUS_APPROVED,
                                then="reviews__rating",
                            ),
                        ),
                    ),
                    Value(0.0),
                ),
                review_count=Count(
                    Case(
                        When(
                            reviews__status=CoachReview.STATUS_APPROVED,
                            then=1,
                        ),
                    ),
                ),
                five_star_count=Count(
                    Case(
                        When(
                            reviews__status=CoachReview.STATUS_APPROVED,
                            reviews__rating=5,
                            then=1,
                        ),
                    ),
                ),
                four_star_count=Count(
                    Case(
                        When(
                            reviews__status=CoachReview.STATUS_APPROVED,
                            reviews__rating=4,
                            then=1,
                        ),
                    ),
                ),
                three_star_count=Count(
                    Case(
                        When(
                            reviews__status=CoachReview.STATUS_APPROVED,
                            reviews__rating=3,
                            then=1,
                        ),
                    ),
                ),
                two_star_count=Count(
                    Case(
                        When(
                            reviews__status=CoachReview.STATUS_APPROVED,
                            reviews__rating=2,
                            then=1,
                        ),
                    ),
                ),
                one_star_count=Count(
                    Case(
                        When(
                            reviews__status=CoachReview.STATUS_APPROVED,
                            reviews__rating=1,
                            then=1,
                        ),
                    ),
                ),
            )
            .select_related("user", "category")
            .prefetch_related("subcategory"),
        ),
    )
    serializer_class = EventDetailSerializer
    lookup_field = "slug"


@extend_schema(
    summary="List and Create Saved Events",
    description="Get a paginated list of saved events for the authenticated user and create new saved events.",  # noqa: E501
    responses={
        200: OpenApiResponse(
            description="List of saved events",
            response=SavedEventListSerializer,
        ),
        201: OpenApiResponse(
            description="Saved event created successfully",
            response=SavedEventListSerializer,
        ),
        400: OpenApiResponse(description="Bad request"),
        404: OpenApiResponse(description="Event not found"),
    },
)
class SavedEventListCreateAPIView(ListCreateAPIView):
    """
    SavedEventListCreateAPIView is a view that provides a paginated list of saved events
    and allows users to create new saved events.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = SavedEventListSerializer
    filter_backends = [OrderingFilter]
    filterset_fields = [
        "event__type",
        "event__location",
        "event__coach",
        "event__coach__uuid",
        "event__coach__category",
        "event__coach__category__name",
        "event__coach__subcategory",
        "event__coach__subcategory__name",
        "event__coach__verification_status",
        "event__coach__experience_level",
    ]
    ordering_fields = [
        "event__name",
        "event__start_datetime",
        "event__end_datetime",
        "event__coach__first_name",
        "event__coach__last_name",
        "event__coach__category__name",
        "event__coach__subcategory__name",
        "created_at",
    ]
    ordering = ["event__start_datetime", "event__end_datetime", "-created_at"]

    def get_queryset(self):
        """
        Returns a queryset of saved events for the authenticated user.
        """
        user = self.request.user
        return (
            user.saved_events.all()
            .select_related("event")
            .prefetch_related(
                "event__tickets",
                Prefetch(
                    "event__coach",
                    queryset=Coach.objects.annotate(
                        avg_rating=Coalesce(
                            Avg(
                                Case(
                                    When(
                                        reviews__status=CoachReview.STATUS_APPROVED,
                                        then="reviews__rating",
                                    ),
                                ),
                            ),
                            Value(0.0),
                        ),
                        review_count=Count(
                            Case(
                                When(
                                    reviews__status=CoachReview.STATUS_APPROVED,
                                    then=1,
                                ),
                            ),
                        ),
                    )
                    .select_related("user", "category")
                    .prefetch_related("subcategory"),
                ),
            )
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddSavedEventSerializer

        return SavedEventListSerializer

    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a new saved event for the authenticated user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_uuid = serializer.validated_data.get("event_uuid")

        try:
            event = Event.objects.get(uuid=event_uuid)

            # Check if the event is already saved by the user
            if request.user.saved_events.filter(event=event).exists():
                return Response(
                    {"detail": "Event already saved."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create the saved event
            saved_event = request.user.saved_events.create(event=event)

            # Return the saved event data
            saved_event_serializer = SavedEventListSerializer(
                saved_event,
                context={"request": request},
            )
            return Response(saved_event_serializer.data, status=status.HTTP_201_CREATED)
        except Event.DoesNotExist:
            return Response(
                {"detail": "Event not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:  # noqa: BLE001
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    summary="Remove Saved Event",
    description="Remove a saved event for the authenticated user.",
    responses={
        204: OpenApiResponse(description="Saved event removed successfully"),
        404: OpenApiResponse(description="Saved event not found"),
    },
)
class RemoveSavedEventAPIView(APIView):
    """
    RemoveSavedEventAPIView is a view that allows users to remove a saved event.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, uuid):
        """
        Handles the deletion of a saved event for the authenticated user.
        """
        try:
            saved_event = request.user.saved_events.get(uuid=uuid)
            saved_event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SavedEvent.DoesNotExist:
            return Response(
                {"detail": "Saved event not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:  # noqa: BLE001
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
