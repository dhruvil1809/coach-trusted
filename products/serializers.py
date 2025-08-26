from rest_framework import serializers

from coach.serializers import CoachDetailSerializer
from coach.serializers import CoachListSerializer

from .models import Product
from .models import ProductCategory
from .models import ProductMedia
from .models import ProductType
from .models import SavedProduct


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductCategory model.
    """

    class Meta:
        model = ProductCategory
        fields = ["id", "name", "slug"]


class ProductTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductType model.
    """

    class Meta:
        model = ProductType
        fields = ["id", "name"]


class MediaSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductMedia model.
    """

    class Meta:
        model = ProductMedia
        fields = ["id", "media_file", "created_at"]


class ProductListSerializer(serializers.ModelSerializer):
    coach = CoachListSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    product_type = ProductTypeSerializer(read_only=True)
    media = MediaSerializer(many=True, read_only=True)

    is_saved = serializers.SerializerMethodField(
        read_only=True,
        help_text="Is the product saved by the user?",
    )
    is_saved_uuid = serializers.SerializerMethodField(
        read_only=True,
        help_text="UUID of the saved product record if saved by the user",
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "uuid",
            "slug",
            "name",
            "description",
            "image",
            "price",
            "language",
            "is_featured",
            "external_url",
            "release_date",
            "ct_id",
            "product_id",
            "is_saved",
            "is_saved_uuid",
            "created_at",
            "updated_at",
            "coach",
            "category",
            "product_type",
            "media",
        ]

    def get_is_saved(self, obj):
        """
        Check if the current product is saved by the authenticated user.
        This method determines whether the current product (obj) has been saved by
        the currently authenticated user. It uses the SavedProduct model to check
        for an existing relationship between the user and the product.
        Args:
            obj: The product instance being serialized.
        Returns:
            bool: True if the authenticated user has saved this product, False otherwise.
                  Always returns False for unauthenticated users.
        """  # noqa: E501

        request = self.context.get("request")
        if (
            not request
            or not hasattr(request, "user")
            or not request.user.is_authenticated
        ):
            # Store None to indicate no authenticated user
            obj.saved_product_instance = None
            return False

        # Cache the saved product instance for use in get_is_saved_uuid
        saved_product = SavedProduct.objects.filter(
            user=request.user,
            product=obj,
        ).first()
        if saved_product:
            # Store the saved product instance in the object for later use
            obj.saved_product_instance = saved_product
            return True

        # Store None to indicate we checked and found nothing
        obj.saved_product_instance = None
        return False

    def get_is_saved_uuid(self, obj):
        """
        Get the UUID of the saved product record if saved by the user.
        This method retrieves the UUID of the SavedProduct record associated with
        the currently authenticated user and the given product (obj). If the product
        is not saved by the user, it returns None.
        Args:
            obj: The product instance being serialized.
        Returns:
            UUID|None: The UUID of the saved product record if it exists, None otherwise.
        """  # noqa: E501

        # If get_is_saved hasn't been called yet, call it to populate the cache
        if not hasattr(obj, "saved_product_instance"):
            self.get_is_saved(obj)

        # Return the cached UUID if available
        if hasattr(obj, "saved_product_instance") and obj.saved_product_instance:
            return str(obj.saved_product_instance.uuid)
        return None


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a product.
    """

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        source="category",
        required=True,
    )
    product_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductType.objects.all(),
        source="product_type",
        required=False,
        allow_null=True,
    )
    media_files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "image",
            "price",
            "language",
            "is_featured",
            "external_url",
            "release_date",
            "ct_id",
            "product_id",
            "category_id",
            "product_type_id",
            "media_files",
        ]
        extra_kwargs = {
            "media": {"required": False},
        }


class ProductDetailSerializer(serializers.ModelSerializer):
    coach = CoachDetailSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    product_type = ProductTypeSerializer(read_only=True)
    media = MediaSerializer(many=True, read_only=True)

    is_saved = serializers.SerializerMethodField(
        read_only=True,
        help_text="Is the product saved by the user?",
    )
    is_saved_uuid = serializers.SerializerMethodField(
        read_only=True,
        help_text="UUID of the saved product record if saved by the user",
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "uuid",
            "slug",
            "name",
            "description",
            "image",
            "price",
            "language",
            "is_featured",
            "external_url",
            "release_date",
            "ct_id",
            "product_id",
            "is_saved",
            "is_saved_uuid",
            "created_at",
            "updated_at",
            "coach",
            "category",
            "product_type",
            "media",
        ]

    def get_is_saved(self, obj):
        """
        Check if the current product is saved by the authenticated user.
        This method determines whether the current product (obj) has been saved by
        the currently authenticated user. It uses the SavedProduct model to check
        for an existing relationship between the user and the product.
        Args:
            obj: The product instance being serialized.
        Returns:
            bool: True if the authenticated user has saved this product, False otherwise.
                  Always returns False for unauthenticated users.
        """  # noqa: E501

        request = self.context.get("request")
        if (
            not request
            or not hasattr(request, "user")
            or not request.user.is_authenticated
        ):
            # Store None to indicate no authenticated user
            obj.saved_product_instance = None
            return False

        # Cache the saved product instance for use in get_is_saved_uuid
        saved_product = SavedProduct.objects.filter(
            user=request.user,
            product=obj,
        ).first()
        if saved_product:
            # Store the saved product instance in the object for later use
            obj.saved_product_instance = saved_product
            return True

        # Store None to indicate we checked and found nothing
        obj.saved_product_instance = None
        return False

    def get_is_saved_uuid(self, obj):
        """
        Get the UUID of the saved product record if the product is saved by the
        authenticated user.
        Args:
            obj: The product instance being serialized.
        Returns:
            str: The UUID of the SavedProduct record if the product is saved,
                 None otherwise.
        """
        # If get_is_saved hasn't been called yet, call it to populate the cache
        if not hasattr(obj, "saved_product_instance"):
            self.get_is_saved(obj)

        # Return the cached UUID if available
        if hasattr(obj, "saved_product_instance") and obj.saved_product_instance:
            return str(obj.saved_product_instance.uuid)
        return None


class ProductUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a product.
    """

    # Remove media field from here since we're handling it separately

    # Explicitly add category_id field
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        source="category",
        required=False,
    )

    product_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductType.objects.all(),
        source="product_type",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "image",
            "price",
            "language",
            "is_featured",
            "external_url",
            "release_date",
            "ct_id",
            "product_id",
            "category_id",
            "product_type_id",
        ]
        extra_kwargs = {
            "image": {"required": False},
            "media": {"required": False},
        }

    def update(self, instance, validated_data):
        """
        Update the product instance with the provided data.
        """
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.image = validated_data.get("image", instance.image)
        instance.price = validated_data.get("price", instance.price)
        instance.language = validated_data.get("language", instance.language)
        instance.is_featured = validated_data.get("is_featured", instance.is_featured)
        instance.external_url = validated_data.get(
            "external_url",
            instance.external_url,
        )
        instance.release_date = validated_data.get(
            "release_date",
            instance.release_date,
        )
        instance.ct_id = validated_data.get("ct_id", instance.ct_id)
        instance.product_id = validated_data.get("product_id", instance.product_id)

        # Explicitly handle category assignment
        if "category" in validated_data:
            instance.category = validated_data.get("category")

        # Explicitly handle product_type assignment
        if "product_type" in validated_data:
            instance.product_type = validated_data.get("product_type")

        instance.save()
        return instance


class ProductMediaManageSerializer(serializers.Serializer):
    """
    Serializer for managing product media files (add/delete).
    """

    media_files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True,
    )
    delete_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )


class SavedProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing saved products.
    """

    product = ProductListSerializer(read_only=True)

    class Meta:
        model = SavedProduct
        fields = ["uuid", "product", "created_at"]


class AddSavedProductSerializer(serializers.Serializer):
    """
    Serializer for adding a saved product.
    """

    product_uuid = serializers.UUIDField(
        required=True,
        help_text="UUID of the product to be saved",
    )
