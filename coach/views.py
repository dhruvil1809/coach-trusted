from django.db.models import Avg
from django.db.models import Case
from django.db.models import Count
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import CoachFilter
from .models import Category
from .models import Coach
from .models import CoachReview
from .models import SavedCoach
from .models import SocialMediaLink
from .models import SubCategory
from .serializers import CategorySerializer
from .serializers import CategoryWithSubCategoriesSerializer
from .serializers import ClaimCoachRequestSerializer
from .serializers import CoachDetailSerializer
from .serializers import CoachListSerializer
from .serializers import CoachReviewListSerializer
from .serializers import CoachReviewSerializer
from .serializers import CreateCoachSerializer
from .serializers import CreateSavedCoachSerializer
from .serializers import SavedCoachSerializer
from .serializers import SocialMediaLinkSerializer
from .serializers import SubCategorySerializer
from .serializers import UpdateCoachSerializer


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(
    summary="List Coaches",
    description="Get a paginated list of all coaches with filtering and search options.",  # noqa: E501
    responses={
        200: OpenApiResponse(
            description="List of coaches",
            response=CoachListSerializer,
        ),
    },
)
class CoachListAPIView(ListAPIView):
    serializer_class = CoachListSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CoachFilter
    search_fields = [
        "first_name",
        "last_name",
    ]
    ordering_fields = [
        "created_at",
        "first_name",
        "last_name",
        "avg_rating",
        "review_count",
        "category__name",
        "subcategory__name",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Get the list of coaches with annotations for average rating and review count.
        Only includes approved coaches and approved reviews in the calculations.
        """
        return (
            Coach.objects.filter(review_status=Coach.REVIEW_APPROVED)
            .select_related("user", "category")
            .prefetch_related("subcategory")
            .annotate(
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
                    Case(When(reviews__status=CoachReview.STATUS_APPROVED, then=1)),
                ),
            )
        )


@extend_schema(
    summary="Retrieve or Update Coach",
    description="Get details of a specific coach or update coach information if authenticated as the owner.",  # noqa: E501
    request=UpdateCoachSerializer,
    responses={
        200: OpenApiResponse(
            description="Coach details",
            response=CoachDetailSerializer,
        ),
        403: OpenApiResponse(
            description="Permission denied - you are not the owner of this coach profile",  # noqa: E501
        ),
        404: OpenApiResponse(
            description="Coach not found",
        ),
    },
)
class CoachRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    lookup_field = "uuid"

    def get_serializer_class(self):
        """
        Return different serializers for GET vs PUT/PATCH operations.
        """
        if self.request.method == "GET":
            return CoachDetailSerializer
        return UpdateCoachSerializer

    def get_queryset(self):
        """
        Get the queryset with annotations for average rating and review count.
        Only includes approved coaches and approved reviews in the calculations.
        """
        return (
            Coach.objects.filter(review_status=Coach.REVIEW_APPROVED)
            .select_related("user", "category")
            .prefetch_related("subcategory")
            .annotate(
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
                    Case(When(reviews__status=CoachReview.STATUS_APPROVED, then=1)),
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
        )

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_object(self):
        obj = super().get_object()
        if self.request.method != "GET" and (
            obj.user is None or obj.user != self.request.user
        ):
            msg = "You do not have permission to access this object."
            raise PermissionDenied(msg)
        return obj

    def update(self, request, *args, **kwargs):
        """
        Override update to use UpdateCoachSerializer for processing
        but CoachDetailSerializer for response.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Use UpdateCoachSerializer for processing the update
        update_serializer = UpdateCoachSerializer(
            instance,
            data=request.data,
            partial=partial,
            context=self.get_serializer_context(),
        )
        update_serializer.is_valid(raise_exception=True)
        updated_instance = update_serializer.save()

        # Refresh the instance to get the updated queryset annotations
        updated_instance = self.get_queryset().get(pk=updated_instance.pk)

        # Use CoachDetailSerializer for the response
        response_serializer = CoachDetailSerializer(
            updated_instance,
            context=self.get_serializer_context(),
        )

        return Response(response_serializer.data)


@extend_schema(
    summary="List Saved Coaches",
    description="Get a paginated list of all saved coaches for the authenticated user.",
    responses={
        200: OpenApiResponse(
            description="List of saved coaches",
            response=SavedCoachSerializer,
        ),
    },
)
class SavedCoachListAPIView(ListAPIView):
    """
    API view to list all saved coaches for the authenticated user.
    """

    serializer_class = SavedCoachSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["created_at", "coach__first_name", "coach__last_name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        return SavedCoach.objects.filter(
            user=user,
            coach__review_status=Coach.REVIEW_APPROVED,
        ).select_related("coach")


@extend_schema(
    summary="Save Coach",
    description="Save a coach to the authenticated user's saved coaches list.",
    request=CreateSavedCoachSerializer,
    responses={
        201: OpenApiResponse(
            description="Coach saved successfully",
            response=SavedCoachSerializer,
        ),
        400: OpenApiResponse(
            description="Bad request - validation error or trying to save own profile",
        ),
        404: OpenApiResponse(
            description="Coach not found",
        ),
        500: OpenApiResponse(
            description="Server error",
        ),
    },
)
class CreateSavedCoachAPIView(CreateAPIView):
    """
    API view to create a new saved coach for the authenticated user.
    """

    serializer_class = CreateSavedCoachSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Create a new saved coach entry for the authenticated user.
        This method allows users to save a coach profile to their collection. It validates
        that the requested coach exists and prevents users from saving their own coach profile.
        Parameters:
            request (Request): The HTTP request object containing user data and coach UUID.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        Returns:
            Response: A response object containing:
                - On success (201): Serialized SavedCoach data
                - On coach not found (404): Error message
                - On attempt to save own profile (400): Error message
                - On other errors (500): Exception details
        Raises:
            Exception: Any unexpected errors during SavedCoach creation are caught
                       and returned as a 500 response.
        """  # noqa: E501

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        coach = serializer.validated_data.get("coach_uuid")

        coach_instance = Coach.objects.filter(
            uuid=coach,
            review_status=Coach.REVIEW_APPROVED,
        ).first()
        if not coach_instance:
            return Response({"detail": "Coach not found."}, status=404)

        if coach_instance.user is not None and coach_instance.user == request.user:
            return Response(
                {"detail": "You cannot save your own coach profile."},
                status=400,
            )

        try:
            saved_coach = SavedCoach.objects.create(
                user=request.user,
                coach=coach_instance,
            )
        except Exception as e:  # noqa: BLE001
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        saved_coach_serializer = SavedCoachSerializer(saved_coach)
        return Response(saved_coach_serializer.data, status=201)


@extend_schema(
    summary="Delete Saved Coach",
    description="Delete a saved coach for the authenticated user.",
    responses={
        204: OpenApiResponse(
            description="Saved coach deleted successfully",
        ),
        404: OpenApiResponse(
            description="Saved coach not found",
        ),
        403: OpenApiResponse(
            description="Permission denied - you are not the owner of this saved coach",
        ),
    },
)
class DeleteSavedCoachAPIView(DestroyAPIView):
    """
    API view to delete a saved coach for the authenticated user.
    """

    permission_classes = [IsAuthenticated]
    queryset = SavedCoach.objects.all()
    lookup_field = "uuid"

    def get_object(self):
        """
        Retrieve the object and verify user permissions.
        Extends the parent class's get_object method by adding a permission check
        to ensure only the owner of the saved coach can access it.
        Raises:
            PermissionDenied: If the requesting user is not the owner of the saved coach.
        Returns:
            The requested object if the user has permission.
        """  # noqa: E501

        obj = super().get_object()
        if obj.user != self.request.user:
            msg = "You do not have permission to delete this saved coach."
            raise PermissionDenied(msg)
        return obj


@extend_schema(
    summary="Claim Coach",
    description="Submit a request to claim a coach profile. If authenticated, the request will be associated with the user.",  # noqa: E501
    request=ClaimCoachRequestSerializer,
    responses={
        201: OpenApiResponse(
            description="Claim request submitted successfully",
        ),
        400: OpenApiResponse(
            description="Bad request - validation error, coach already claimed, or user already has a coach profile",  # noqa: E501
        ),
        404: OpenApiResponse(
            description="Coach not found",
        ),
        500: OpenApiResponse(
            description="Server error",
        ),
    },
)
class ClaimCoachRequestCreateAPIView(CreateAPIView):
    """
    API view to submit a request to claim a coach profile.
    """

    serializer_class = ClaimCoachRequestSerializer

    def get_permissions(self):
        """
        Allow anonymous users to submit claim requests,
        but if a user is authenticated, the request will be associated with them.
        """
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        """
        Create a new claim request for a coach profile.
        This method handles the creation of a claim request for a coach profile. If the user
        is authenticated, the request will be associated with their account. Otherwise,
        the request will be anonymous and the user will need to create an account later.

        Parameters:
            request: The HTTP request object containing the claim data
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            Response: A response object with the status of the claim request creation
        """  # noqa: E501
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            claim_request = serializer.save()

            # Return a simple success response
            response_data = {
                "detail": "Your claim request has been submitted successfully.",
                "uuid": str(claim_request.uuid),
                "status": claim_request.status,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:  # noqa: BLE001
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    summary="Submit Coach Review",
    description="Submit a review for a coach. If authenticated, the review will be "
    "associated with the user.",
    request=CoachReviewSerializer,
    responses={
        201: OpenApiResponse(
            description="Review submitted successfully",
        ),
        400: OpenApiResponse(
            description="Bad request - validation error",
        ),
        404: OpenApiResponse(
            description="Coach not found",
        ),
        500: OpenApiResponse(
            description="Server error",
        ),
    },
)
class CoachReviewCreateAPIView(CreateAPIView):
    """
    API view to submit a review for a coach.
    """

    serializer_class = CoachReviewSerializer

    def get_permissions(self):
        """
        Allow anonymous users to submit reviews,
        but if a user is authenticated, the review will be associated with them.
        """
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        """
        Create a new review for a coach.
        This method handles the creation of a review for a coach. If the user
        is authenticated, the review will be associated with their account.

        Parameters:
            request: The HTTP request object containing the review data
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            Response: A response object with the status of the review creation
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = serializer.save()

            # Return a simple success response
            response_data = {
                "detail": "Your review has been submitted and is pending approval.",
                "uuid": str(review.uuid),
                "status": review.status,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:  # noqa: BLE001
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    summary="List Coach Reviews",
    description="Get a paginated list of approved coach reviews.",
    responses={
        200: OpenApiResponse(
            description="List of approved coach reviews",
            response=CoachReviewListSerializer,
        ),
        400: OpenApiResponse(
            description="Invalid coach UUID format",
        ),
        404: OpenApiResponse(
            description="Coach not found",
        ),
    },
)
class CoachReviewListAPIView(ListAPIView):
    """
    API view to list approved coach reviews with pagination.
    Only returns reviews with status='approved' for the specified coach.
    """

    serializer_class = CoachReviewListSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["created_at", "rating", "date"]
    ordering = ["-created_at"]

    def get_permissions(self):
        # Allow anyone to view reviews (only approved ones are shown)
        return [AllowAny()]

    def list(self, request, *args, **kwargs):
        """
        Override list method to handle invalid UUID format properly.
        """
        coach_uuid = self.kwargs.get("coach_uuid")
        try:
            # Validate UUID format
            import uuid

            uuid.UUID(str(coach_uuid))
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid coach UUID format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if coach exists and is approved
        coach_exists = Coach.objects.filter(
            uuid=coach_uuid,
            review_status=Coach.REVIEW_APPROVED,
        ).exists()
        if not coach_exists:
            return Response(
                {"detail": "Coach not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Get the list of coach reviews for a specific coach.
        Only shows approved reviews for approved coaches regardless of
        authentication status. Uses the coach_uuid from the URL path to filter reviews.
        """
        coach_uuid = self.kwargs.get("coach_uuid")
        try:
            return CoachReview.objects.filter(
                coach__uuid=coach_uuid,
                coach__review_status=Coach.REVIEW_APPROVED,
                status=CoachReview.STATUS_APPROVED,
            ).select_related("coach")
        except ValueError:
            # Handle invalid UUID format
            return CoachReview.objects.none()


@extend_schema(
    summary="Retrieve or Update Coach Social Media Links",
    description="Get or update social media links for a specific coach. Only the coach owner can update the links.",  # noqa: E501
    responses={
        200: OpenApiResponse(
            description="Coach social media links",
            response=SocialMediaLinkSerializer,
        ),
        400: OpenApiResponse(
            description="Invalid coach UUID format",
        ),
        403: OpenApiResponse(
            description="Permission denied - you are not the owner of this coach profile",  # noqa: E501
        ),
        404: OpenApiResponse(
            description="Coach not found",
        ),
    },
)
class CoachSocialMediaLinksRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    API view to retrieve and update social media links for a coach.
    """

    serializer_class = SocialMediaLinkSerializer
    lookup_field = "coach__uuid"
    lookup_url_kwarg = "coach_uuid"

    def get_queryset(self):
        """
        Get the queryset for social media links.
        """
        return SocialMediaLink.objects.select_related("coach")

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_object(self):
        """
        Get the social media link object for the coach.
        Creates one if it doesn't exist for GET requests.
        Checks permissions for update requests.
        """
        coach_uuid = self.kwargs.get("coach_uuid")

        # Validate UUID format
        try:
            import uuid

            uuid.UUID(str(coach_uuid))
        except (ValueError, TypeError) as err:
            from django.http import Http404

            msg = "Invalid coach UUID format."
            raise Http404(msg) from err

        try:
            if self.request.method == "GET":
                # For GET requests, only show approved coaches
                coach = Coach.objects.get(
                    uuid=coach_uuid,
                    review_status=Coach.REVIEW_APPROVED,
                )
            else:
                # For update requests, allow any coach (owner will be validated later)
                coach = Coach.objects.get(uuid=coach_uuid)
        except Coach.DoesNotExist as err:
            from django.http import Http404

            msg = "Coach not found."
            raise Http404(msg) from err

        # For update requests, check if user owns the coach
        if self.request.method != "GET":
            if coach.user is None or coach.user != self.request.user:
                msg = "You do not have permission to update this coach's social media links."  # noqa: E501
                raise PermissionDenied(msg)

        # Get or create social media links for the coach
        social_media_link, created = SocialMediaLink.objects.get_or_create(
            coach=coach,
        )

        return social_media_link


@extend_schema(
    summary="List Categories",
    description="Get a list of all coach categories. Results are cached for 5 minutes to improve performance.",  # noqa: E501
    responses={
        200: OpenApiResponse(
            description="List of categories",
            response=CategorySerializer,
        ),
    },
)
@method_decorator(cache_page(300), name="dispatch")  # Cache for 5 minutes
class CategoryListAPIView(ListAPIView):
    """
    API view to list all categories.

    This endpoint returns all available coach categories
    without pagination. Useful for populating filter dropdowns or forms.
    """

    serializer_class = CategoryWithSubCategoriesSerializer
    authentication_classes = []
    permission_classes = []
    pagination_class = None  # Disable pagination

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "name",
    ]
    ordering_fields = ["name"]
    ordering = ["name"]

    def get_queryset(self):
        """Return all categories ordered by name."""
        return Category.objects.all().order_by("name")


@extend_schema(
    summary="List Subcategories",
    description="Get a list of all coach subcategories. Results are cached for 5 minutes to improve performance.",  # noqa: E501
    responses={
        200: OpenApiResponse(
            description="List of subcategories",
            response=SubCategorySerializer,
        ),
    },
)
@method_decorator(cache_page(300), name="dispatch")  # Cache for 5 minutes
class SubCategoryListAPIView(ListAPIView):
    """
    API view to list all subcategories.

    This endpoint returns all available coach subcategories
    without pagination. Useful for populating filter dropdowns or forms.
    """

    serializer_class = SubCategorySerializer
    authentication_classes = []
    permission_classes = []
    pagination_class = None  # Disable pagination

    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["name", "category__name"]
    ordering_fields = ["name", "category__name"]
    filterset_fields = ["category", "category__name", "category__uuid"]
    ordering = ["name"]

    def get_queryset(self):
        """Return all subcategories with category data."""
        return SubCategory.objects.all().select_related("category")


@extend_schema(
    summary="Create Coach Profile",
    description="Create a new coach profile for the authenticated user. "
    "The user must be authenticated and cannot already have an existing coach profile.",
    request=CreateCoachSerializer,
    responses={
        201: OpenApiResponse(
            description="Coach profile created successfully",
            response=CoachDetailSerializer,
        ),
        400: OpenApiResponse(
            description="Bad request - validation error, user already has a coach profile, or profile is under review",  # noqa: E501
        ),
        401: OpenApiResponse(
            description="Authentication required",
        ),
        500: OpenApiResponse(
            description="Server error",
        ),
    },
)
class CreateCoachAPIView(CreateAPIView):
    """
    API view to create a new coach profile.
    This view allows authenticated users to create a new coach profile.
    It requires the user to be authenticated and provides validation for the input data.
    """

    serializer_class = CreateCoachSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to create a new coach profile.
        This method validates the input data and creates a new coach profile
        associated with the authenticated user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if (
            hasattr(request.user, "coach")
            and request.user.coach.review_status == Coach.REVIEW_PENDING
        ):
            return Response(
                {"detail": "Your coach profile is still under review."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            hasattr(request.user, "coach")
            and request.user.coach.review_status == Coach.REVIEW_APPROVED
        ):
            return Response(
                {"detail": "You already have a coach profile."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = serializer.validated_data.get("category")
        category_instance = Category.objects.filter(
            name=category,
        ).first()
        subcategory = serializer.validated_data.get("subcategory")
        subcategory_instance = SubCategory.objects.filter(name__in=subcategory)

        coach = Coach.objects.create(
            user=request.user,
            first_name=serializer.validated_data.get("first_name"),
            last_name=serializer.validated_data.get("last_name", ""),
            website=serializer.validated_data.get("website"),
            type=serializer.validated_data.get("type"),
            email=serializer.validated_data.get("email"),
            country=serializer.validated_data.get("country"),
            category=category_instance,
            phone_number=serializer.validated_data.get("phone_number"),
            location=serializer.validated_data.get("location"),
            review_status=Coach.REVIEW_PENDING,
        )
        coach.subcategory.set(subcategory_instance)
        coach.save()

        # Return the serialized data of the created coach profile
        return Response(
            CoachDetailSerializer(coach).data,
            status=status.HTTP_201_CREATED,
        )
