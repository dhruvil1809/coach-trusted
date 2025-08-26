from django.db import transaction
from django.db.models import Avg
from django.db.models import Case
from django.db.models import Count
from django.db.models import Prefetch
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Coalesce
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from rest_framework import filters
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from coach.models import Coach
from coach.models import CoachReview

from .filters import ProductFilter
from .models import Product
from .models import ProductMedia
from .models import SavedProduct
from .serializers import AddSavedProductSerializer
from .serializers import MediaSerializer
from .serializers import ProductCreateSerializer
from .serializers import ProductDetailSerializer
from .serializers import ProductListSerializer
from .serializers import ProductMediaManageSerializer
from .serializers import ProductUpdateSerializer
from .serializers import SavedProductListSerializer


class CustomPagination(PageNumberPagination):
    """
    Custom pagination class to handle page size and maximum page size.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(
    methods=["GET"],
    summary="List Products",
    description="Get a paginated list of all products with filtering (including price range), ordering and search options.",  # noqa: E501
    responses={
        200: OpenApiResponse(
            description="List of products",
            response=ProductListSerializer,
        ),
    },
    parameters=[
        {
            "name": "page",
            "in": "query",
            "description": "Page number",
            "required": False,
            "type": "integer",
        },
        {
            "name": "page_size",
            "in": "query",
            "description": "Number of results per page (max 100)",
            "required": False,
            "type": "integer",
        },
        {
            "name": "search",
            "in": "query",
            "description": "Search term for name, description, coach name, category name or product type name",  # noqa: E501
            "required": False,
            "type": "string",
        },
        {
            "name": "language",
            "in": "query",
            "description": "Filter by product language (en, es, fr, de, it)",
            "required": False,
            "type": "string",
        },
        {
            "name": "product_type__id",
            "in": "query",
            "description": "Filter by product type ID",
            "required": False,
            "type": "integer",
        },
        {
            "name": "product_type__name",
            "in": "query",
            "description": "Filter by product type name",
            "required": False,
            "type": "string",
        },
        {
            "name": "category__id",
            "in": "query",
            "description": "Filter by category ID",
            "required": False,
            "type": "integer",
        },
        {
            "name": "is_featured",
            "in": "query",
            "description": "Filter by featured status (true/false)",
            "required": False,
            "type": "boolean",
        },
        {
            "name": "price",
            "in": "query",
            "description": "Filter by exact price",
            "required": False,
            "type": "number",
        },
        {
            "name": "price__gte",
            "in": "query",
            "description": "Filter by price greater than or equal to this value",
            "required": False,
            "type": "number",
        },
        {
            "name": "price__lte",
            "in": "query",
            "description": "Filter by price less than or equal to this value",
            "required": False,
            "type": "number",
        },
    ],
)
@extend_schema(
    methods=["POST"],
    summary="Create Product",
    description="Create a new product with optional media files. Only authenticated coaches can create products.",  # noqa: E501
    request=ProductCreateSerializer,
    responses={
        201: OpenApiResponse(
            description="Product created successfully",
            response=ProductDetailSerializer,
        ),
    },
)
class ProductListCreateAPIView(ListCreateAPIView):
    """
    API view to retrieve and create products.
    """

    queryset = (
        Product.objects.all()
        .order_by("-created_at")
        .select_related("category", "product_type")
        .prefetch_related(
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
                .select_related("category")
                .prefetch_related("subcategory"),
            ),
        )
    )
    pagination_class = CustomPagination
    serializer_class = ProductListSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = ProductFilter
    ordering_fields = ["created_at", "updated_at", "name", "price"]
    search_fields = [
        "name",
        "description",
        "coach__first_name",
        "coach__last_name",
        "category__name",
        "product_type__name",
    ]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProductListSerializer
        if self.request.method == "POST":
            return ProductCreateSerializer
        return ProductListSerializer

    def get_permissions(self):
        """
        Allow anyone to list products, but require authentication to create.
        """
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """
        Override create to use ProductDetailSerializer for response
        """
        # Use ProductCreateSerializer for input validation (handled by get_serializer_class)  # noqa: E501
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        # Use ProductDetailSerializer for the response
        detail_serializer = ProductDetailSerializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(
            detail_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        """
        Override perform_create to automatically set coach from the authenticated user
        and handle media files.
        """
        if not hasattr(self.request.user, "coach"):
            msg = "You must be a coach to create products."
            raise PermissionDenied(msg)

        # Get media files from validated data
        media_files = serializer.validated_data.pop("media_files", [])

        # Save the product with the coach set
        product = serializer.save(coach=self.request.user.coach)

        # Create ProductMedia instances for each media file
        for media_file in media_files:
            ProductMedia.objects.create(product=product, media_file=media_file)

        return product


@extend_schema(
    methods=["GET"],
    summary="Retrieve Product",
    description="Get details of a specific product by its slug.",
    responses={
        200: OpenApiResponse(
            description="Product details",
            response=ProductDetailSerializer,
        ),
    },
)
@extend_schema(
    methods=["PUT"],
    summary="Update Product",
    description="Update a product. Only the coach who owns the product can update it.",
    request=ProductUpdateSerializer,
    responses={
        200: OpenApiResponse(
            description="Product updated successfully",
            response=ProductDetailSerializer,
        ),
    },
)
@extend_schema(
    methods=["PATCH"],
    summary="Partially Update Product",
    description="Partially update a product. Only the coach who owns the product can update it.",  # noqa: E501
    request=ProductUpdateSerializer,
    responses={
        200: OpenApiResponse(
            description="Product partially updated successfully",
            response=ProductDetailSerializer,
        ),
    },
)
class ProductRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    API view to retrieve and update a product.

    GET: Any user can retrieve product details
    PUT/PATCH: Only the coach who owns the product can update it
    """

    queryset = (
        Product.objects.all()
        .order_by("-created_at")
        .select_related("category", "product_type")
        .prefetch_related(
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
                .select_related("category")
                .prefetch_related("subcategory"),
            ),
        )
    )
    lookup_field = "slug"

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProductDetailSerializer
        if self.request.method in ["PUT", "PATCH"]:
            return ProductUpdateSerializer
        return ProductListSerializer

    def get_object(self):
        obj = super().get_object()
        # Allow read access to everyone
        if self.request.method != "GET":
            # For update operations, verify the requesting user is the coach who owns the product  # noqa: E501
            if (
                not hasattr(self.request.user, "coach")
                or obj.coach != self.request.user.coach
            ):
                msg = "You do not have permission to update this product."
                raise PermissionDenied(
                    msg,
                )
        return obj

    def update(self, request, *args, **kwargs):
        """
        Override update to use ProductDetailSerializer for response
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Use ProductUpdateSerializer for validating input data
        update_serializer = ProductUpdateSerializer(
            instance,
            data=request.data,
            partial=partial,
        )
        update_serializer.is_valid(raise_exception=True)
        self.perform_update(update_serializer)

        # Use ProductDetailSerializer for response
        detail_serializer = ProductDetailSerializer(instance)
        return Response(detail_serializer.data)

    def perform_update(self, serializer):
        serializer.save()


@extend_schema(
    methods=["GET"],
    summary="Retrieve Product Media",
    description="Get all media files associated with a product",
    responses={
        200: OpenApiResponse(
            description="List of product media files",
            response=MediaSerializer(many=True),
        ),
        404: OpenApiResponse(description="Product not found"),
    },
)
@extend_schema(
    methods=["POST"],
    summary="Manage Product Media",
    description="Add new media files and/or delete existing media by ID. Only the coach who owns the product can modify media.",  # noqa: E501
    request=ProductMediaManageSerializer,
    responses={
        200: OpenApiResponse(
            description="Updated list of product media files",
            response=MediaSerializer(many=True),
        ),
        400: OpenApiResponse(description="Bad request - invalid input data"),
        403: OpenApiResponse(description="Permission denied"),
        404: OpenApiResponse(description="Product not found"),
    },
)
class ProductMediaUpdateAPIView(APIView):
    """
    API view to manage media files associated with a product.

    GET: Retrieve all media files for a product
    POST: Add new media files and/or delete existing media files by ID
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        """
        Allow anyone to view media files, but require authentication for modifying them.
        """
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_product(self, slug):
        """Helper to get product by slug or raise 404"""
        try:
            return Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            msg = "Product not found"
            raise Http404(msg)  # noqa: B904

    def get(self, request, slug):
        """Retrieve all media for a product"""
        product = self.get_product(slug)
        media = product.media.all()
        serializer = MediaSerializer(media, many=True)
        return Response(serializer.data)

    def post(self, request, slug):
        """Add new media files and/or delete existing media for a product"""
        product = self.get_product(slug)

        # Check permissions
        if not hasattr(request.user, "coach") or product.coach != request.user.coach:
            return Response(
                {
                    "detail": "You don't have permission to modify media for this product",  # noqa: E501
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Validate input data
        serializer = ProductMediaManageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Process deletions
            delete_ids = serializer.validated_data.get("delete_ids", [])
            if delete_ids:
                deleted_count = ProductMedia.objects.filter(
                    id__in=delete_ids,
                    product=product,
                ).delete()[0]
                if deleted_count == 0 and delete_ids:
                    # Optional: Warn if no files were actually deleted
                    pass

            # Process additions
            media_files = serializer.validated_data.get("media_files", [])
            if media_files:
                media_objects = [
                    ProductMedia(product=product, media_file=media_file)
                    for media_file in media_files
                ]
                ProductMedia.objects.bulk_create(media_objects)

        # Return updated media collection
        media = product.media.all()
        response_serializer = MediaSerializer(media, many=True)
        return Response(response_serializer.data)


@extend_schema(
    methods=["GET"],
    summary="List Saved Products",
    description="Get a paginated list of saved products for the authenticated user.",
    responses={
        200: OpenApiResponse(
            description="List of saved products",
            response=SavedProductListSerializer,
        ),
    },
)
@extend_schema(
    methods=["POST"],
    summary="Create Saved Product",
    description="Save a product for the authenticated user.",
    request=AddSavedProductSerializer,
    responses={
        201: OpenApiResponse(
            description="Saved product created successfully",
            response=SavedProductListSerializer,
        ),
        400: OpenApiResponse(
            description="Bad request - product already saved or validation error",
        ),
        404: OpenApiResponse(
            description="Product not found",
        ),
        500: OpenApiResponse(
            description="Server error",
        ),
    },
)
class SavedProductListCreateAPIView(ListCreateAPIView):
    """
    API view to list and create saved products for the authenticated user.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["product__category__id", "product__category__slug"]
    ordering_fields = ["product__name", "product__price", "created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return self.request.user.saved_products.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddSavedProductSerializer

        return SavedProductListSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new saved product entry for the authenticated user.
        This method allows users to save a product to their collection. It validates
        that the requested product exists and prevents users from saving a product
        that's already in their saved products.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get product from validated data
        product_uuid = serializer.validated_data.get("product_uuid")

        try:
            # Get the product instance
            product = Product.objects.get(uuid=product_uuid)

            # Check if product is already saved by this user
            if request.user.saved_products.filter(product=product).exists():
                return Response(
                    {"detail": "You have already saved this product."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create the saved product
            saved_product = request.user.saved_products.create(product=product)

            # Return the saved product details
            response_serializer = SavedProductListSerializer(
                saved_product,
                context={"request": request},
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:  # noqa: BLE001
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    summary="Delete Saved Product",
    description="Remove a product from the authenticated user's saved products list.",
    responses={
        204: OpenApiResponse(
            description="Saved product deleted successfully",
        ),
        404: OpenApiResponse(
            description="Saved product not found",
        ),
    },
)
class RemoveSavedProductAPIView(APIView):
    """
    API view to remove a saved product for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, uuid):
        """
        Delete a saved product for the authenticated user.
        This method removes a product from the user's saved products list using the provided UUID.
        Parameters:
        ----------
        request : Request
            The HTTP request object containing the authenticated user.
        uuid : str
            The unique identifier of the product to be removed from saved products.
        Returns:
        -------
        Response
            - 204 NO_CONTENT: If the saved product was successfully deleted.
            - 404 NOT_FOUND: If no saved product with the given UUID exists for the user.
        """  # noqa: E501

        try:
            saved_product = request.user.saved_products.get(product__uuid=uuid)
            saved_product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SavedProduct.DoesNotExist:
            return Response(
                {"detail": "Saved product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
