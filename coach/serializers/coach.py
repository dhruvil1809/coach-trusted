from django.conf import settings
from django.db import transaction
from rest_framework import serializers

from coach.models import Coach
from coach.models import CoachMedia
from coach.models import SavedCoach
from coach.serializers.category import CategorySerializer
from coach.serializers.category import SubCategorySerializer
from coach.serializers.coach_media import CoachMediaSerializer


class CoachListSerializer(serializers.ModelSerializer):
    is_claimable = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    is_saved_uuid = serializers.SerializerMethodField()
    avg_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(many=True, read_only=True)
    total_events = serializers.SerializerMethodField()
    total_products = serializers.SerializerMethodField()

    class Meta:
        model = Coach
        fields = [
            "id",
            "uuid",
            "title",
            "first_name",
            "last_name",
            "profile_picture",
            "cover_image",
            "type",
            "company",
            "street_no",
            "zip_code",
            "city",
            "country",
            "website",
            "email",
            "phone_number",
            "location",
            "category",
            "subcategory",
            "verification_status",
            "experience_level",
            "is_claimable",
            "is_saved",
            "is_saved_uuid",
            "avg_rating",
            "review_count",
            "total_events",
            "total_products",
        ]

    def get_is_claimable(self, obj):
        """
        Determine if a coach profile can be claimed.
        A coach is claimable if it's not already associated with a user.
        """
        return obj.user is None

    def get_is_saved(self, obj):
        """
        Check if the current coach is saved by the authenticated user.
        This method determines whether the current coach (obj) has been saved by
        the currently authenticated user. It uses the SavedCoach model to check
        for an existing relationship between the user and the coach.
        Args:
            obj: The coach instance being serialized.
        Returns:
            bool: True if the authenticated user has saved this coach, False otherwise.
                  Always returns False for unauthenticated users.
        """
        request = self.context.get("request")
        if (
            not request
            or not hasattr(request, "user")
            or not request.user.is_authenticated
        ):
            return False

        # Cache the saved coach instance for use in get_saved_uuid
        saved_coach = SavedCoach.objects.filter(user=request.user, coach=obj).first()
        if saved_coach:
            # Store the saved coach instance in the object for later use
            obj.saved_coach_instance = saved_coach
            return True

        # Store None to indicate we checked and found nothing
        obj.saved_coach_instance = None
        return False

    def get_is_saved_uuid(self, obj):
        """
        Get the UUID of the saved coach record if the coach is saved by the
        authenticated user.
        Args:
            obj: The coach instance being serialized.
        Returns:
            str: The UUID of the SavedCoach record if the coach is saved,
                 None otherwise.
        """
        # If get_is_saved hasn't been called yet, call it to populate the cache
        if not hasattr(obj, "saved_coach_instance"):
            self.get_is_saved(obj)

        # Return the cached UUID if available
        if hasattr(obj, "saved_coach_instance") and obj.saved_coach_instance:
            return str(obj.saved_coach_instance.uuid)
        return None

    def get_total_events(self, obj):
        """
        Get the total number of events associated with the coach.
        """
        return obj.events.count() if hasattr(obj, "events") else 0

    def get_total_products(self, obj):
        """
        Get the total number of products associated with the coach.
        """
        return obj.products.count() if hasattr(obj, "products") else 0

    def to_representation(self, instance):
        """
        Override to provide default cover image when missing.
        """
        data = super().to_representation(instance)

        # If cover_image is None or empty, provide default cover image URL
        if not data.get("cover_image"):
            request = self.context.get("request")
            if request:
                # Build absolute URL for default cover image
                default_cover_url = request.build_absolute_uri(
                    settings.STATIC_URL + "images/coach-cover-image.jpg",
                )
                data["cover_image"] = default_cover_url

        return data


class CoachDetailSerializer(serializers.ModelSerializer):
    is_claimable = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    is_saved_uuid = serializers.SerializerMethodField()
    avg_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    rating_breakdown = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(many=True, read_only=True)
    media = CoachMediaSerializer(many=True, read_only=True)
    total_events = serializers.SerializerMethodField()
    total_products = serializers.SerializerMethodField()

    class Meta:
        model = Coach
        fields = [
            "id",
            "uuid",
            "title",
            "first_name",
            "last_name",
            "profile_picture",
            "cover_image",
            "type",
            "about",
            "company",
            "street_no",
            "zip_code",
            "city",
            "country",
            "website",
            "email",
            "phone_number",
            "location",
            "category",
            "subcategory",
            "verification_status",
            "experience_level",
            "is_claimable",
            "is_saved",
            "is_saved_uuid",
            "avg_rating",
            "review_count",
            "media",
            "rating_breakdown",
            "total_events",
            "total_products",
        ]

    def get_is_claimable(self, obj):
        """
        Determine if a coach profile can be claimed.
        A coach is claimable if it's not already associated with a user.
        """
        return obj.user is None

    def get_is_saved(self, obj):
        """
        Check if the current coach is saved by the authenticated user.
        This method determines whether the current coach (obj) has been saved by
        the currently authenticated user. It uses the SavedCoach model to check
        for an existing relationship between the user and the coach.
        Args:
            obj: The coach instance being serialized.
        Returns:
            bool: True if the authenticated user has saved this coach, False otherwise.
                  Always returns False for unauthenticated users.
        """
        request = self.context.get("request")
        if (
            not request
            or not hasattr(request, "user")
            or not request.user.is_authenticated
        ):
            return False

        # Cache the saved coach instance for use in get_saved_uuid
        saved_coach = SavedCoach.objects.filter(user=request.user, coach=obj).first()
        if saved_coach:
            # Store the saved coach instance in the object for later use
            obj.saved_coach_instance = saved_coach
            return True

        # Store None to indicate we checked and found nothing
        obj.saved_coach_instance = None
        return False

    def get_is_saved_uuid(self, obj):
        """
        Get the UUID of the saved coach record if the coach is saved by the
        authenticated user.
        Args:
            obj: The coach instance being serialized.
        Returns:
            str: The UUID of the SavedCoach record if the coach is saved,
                 None otherwise.
        """
        # If get_is_saved hasn't been called yet, call it to populate the cache
        if not hasattr(obj, "saved_coach_instance"):
            self.get_is_saved(obj)

        # Return the cached UUID if available
        if hasattr(obj, "saved_coach_instance") and obj.saved_coach_instance:
            return str(obj.saved_coach_instance.uuid)
        return None

    def get_rating_breakdown(self, obj):
        """
        Get the count of reviews for each rating (1-5 stars).
        """
        return {
            "5_star": getattr(obj, "five_star_count", 0),
            "4_star": getattr(obj, "four_star_count", 0),
            "3_star": getattr(obj, "three_star_count", 0),
            "2_star": getattr(obj, "two_star_count", 0),
            "1_star": getattr(obj, "one_star_count", 0),
        }

    def get_total_events(self, obj):
        """
        Get the total number of events associated with the coach.
        """
        return obj.events.count() if hasattr(obj, "events") else 0

    def get_total_products(self, obj):
        """
        Get the total number of products associated with the coach.
        """
        return obj.products.count() if hasattr(obj, "products") else 0

    def to_representation(self, instance):
        """
        Override to provide default cover image when missing.
        """
        data = super().to_representation(instance)

        # If cover_image is None or empty, provide default cover image URL
        if not data.get("cover_image"):
            request = self.context.get("request")
            if request:
                # Build absolute URL for default cover image
                default_cover_url = request.build_absolute_uri(
                    settings.STATIC_URL + "images/coach-cover-image.jpg",
                )
                data["cover_image"] = default_cover_url

        return data


class CreateCoachSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    website = serializers.URLField()
    type = serializers.ChoiceField(
        choices=Coach.TYPE_CHOICES,
        default=Coach.TYPE_ONLINE_OFFLINE,
    )
    email = serializers.EmailField()
    country = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=50)
    location = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=100)
    subcategory = serializers.ListField(child=serializers.CharField(max_length=100))

    def validate_category(self, value):
        """
        Validate that the category exists in the database.
        """
        from coach.models import Category

        if not Category.objects.filter(name=value).exists():
            msg = "Category does not exist."
            raise serializers.ValidationError(msg)
        return value

    def validate_subcategory(self, value):
        """
        Validate that all subcategories exist in the database.
        """
        from coach.models import SubCategory

        if not SubCategory.objects.filter(name__in=value).exists():
            msg = "One or more subcategories do not exist."
            raise serializers.ValidationError(msg)
        return value


class UpdateCoachSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Coach instances.
    Handles all updatable coach fields including media file management.
    """

    type = serializers.ChoiceField(
        choices=Coach.TYPE_CHOICES,
        required=False,
        error_messages={
            "invalid_choice": "Invalid coach type '{input}'. Valid options are: 'offline', 'online', 'online_offline'.",  # noqa: E501
        },
    )

    # Media management fields
    media = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True,
        write_only=True,
        help_text="List of media files to upload and associate with the coach",
    )
    delete_media_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        write_only=True,
        help_text="List of media IDs to delete",
    )

    class Meta:
        model = Coach
        fields = [
            "title",
            "first_name",
            "last_name",
            "profile_picture",
            "cover_image",
            "type",
            "about",
            "company",
            "street_no",
            "zip_code",
            "city",
            "country",
            "website",
            "email",
            "phone_number",
            "location",
            "category",
            "subcategory",
            "media",
            "delete_media_ids",
        ]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "title": {"required": False},
            "type": {"required": False},
            "about": {"required": False},
            "company": {"required": False},
            "street_no": {"required": False},
            "zip_code": {"required": False},
            "city": {"required": False},
            "country": {"required": False},
            "website": {"required": False},
            "email": {"required": False},
            "phone_number": {"required": False},
            "location": {"required": False},
            "category": {"required": False},
            "subcategory": {"required": False},
        }

    def update(self, instance, validated_data):
        """
        Update coach instance with support for media file management and category updates.
        """  # noqa: E501
        # Extract media management data
        media_files = validated_data.pop("media", [])
        delete_media_ids = validated_data.pop("delete_media_ids", [])

        # Extract category/subcategory data for special handling
        category = validated_data.pop("category", None)
        subcategories = validated_data.pop("subcategory", None)

        with transaction.atomic():
            # Update basic coach fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            # Update category if provided
            if category is not None:
                instance.category = category

            instance.save()

            # Update subcategories if provided
            if subcategories is not None:
                instance.subcategory.set(subcategories)

            # Process media file deletions
            if delete_media_ids:
                CoachMedia.objects.filter(
                    id__in=delete_media_ids,
                    coach=instance,
                ).delete()

            # Process media file uploads
            if media_files:
                media_objects = [
                    CoachMedia(coach=instance, file=media_file)
                    for media_file in media_files
                ]
                CoachMedia.objects.bulk_create(media_objects)

        return instance

    def validate_category(self, value):
        """
        Validate that the category exists by ID.
        """
        if value is None:
            return value

        from coach.models import Category

        if not Category.objects.filter(id=value.id).exists():
            msg = f"Category with ID {value.id} does not exist."
            raise serializers.ValidationError(msg)
        return value

    def validate_subcategory(self, value):
        """
        Validate that all subcategories exist by ID and optionally belong to the selected category.
        """  # noqa: E501
        if not value:
            return value

        from coach.models import SubCategory

        subcategory_ids = [sub.id for sub in value]
        existing_subcategories = SubCategory.objects.filter(id__in=subcategory_ids)

        if existing_subcategories.count() != len(subcategory_ids):
            existing_ids = list(existing_subcategories.values_list("id", flat=True))
            invalid_ids = [
                sub_id for sub_id in subcategory_ids if sub_id not in existing_ids
            ]
            msg = f"Subcategories with IDs {invalid_ids} do not exist."
            raise serializers.ValidationError(msg)

        return value

    def validate_delete_media_ids(self, value):
        """
        Validate that media IDs exist and belong to the coach being updated.
        """
        if not value:
            return value

        # Ensure they're positive integers
        for media_id in value:
            if media_id <= 0:
                msg = "Media ID must be a positive integer"
                raise serializers.ValidationError(msg)

        # Validate that media IDs belong to the coach being updated
        if self.instance:
            existing_media_ids = list(
                self.instance.media.values_list("id", flat=True),
            )
            invalid_ids = [
                media_id for media_id in value if media_id not in existing_media_ids
            ]
            if invalid_ids:
                msg = f"Media IDs {invalid_ids} do not belong to this coach"
                raise serializers.ValidationError(msg)

        return value
