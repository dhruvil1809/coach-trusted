from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.admin import StackedInline

from coach.models import Category
from coach.models import ClaimCoachRequest
from coach.models import Coach
from coach.models import CoachMedia
from coach.models import CoachReview
from coach.models import SavedCoach
from coach.models import SocialMediaLink
from coach.models import SubCategory


class SocialMediaLinkInline(StackedInline):
    """
    Inline admin for Social Media Links.
    """

    model = SocialMediaLink
    extra = 0
    max_num = 1
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        (
            "Social Media Platforms",
            {
                "fields": (
                    "instagram",
                    "facebook",
                    "linkedin",
                    "youtube",
                    "tiktok",
                    "x",
                ),
            },
        ),
        (
            "Review Platforms",
            {
                "fields": (
                    "trustpilot",
                    "google",
                    "provexpert",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )


class CoachMediaInline(StackedInline):
    """
    Inline admin for Coach Media.
    """

    model = CoachMedia
    extra = 0
    readonly_fields = ("created_at", "file_preview")
    fields = ("file", "file_preview", "created_at")

    @admin.display(
        description="File Preview",
    )
    def file_preview(self, obj):
        """
        Display a preview of media file if it's an image, otherwise show the file name.
        """
        if obj.file:
            file_name = obj.file.name
            file_url = obj.file.url

            # Check if it's an image file
            image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
            if any(file_name.lower().endswith(ext) for ext in image_extensions):
                return format_html(
                    '<img src="{}" style="max-width: 100px; max-height: 100px; '
                    'object-fit: cover;" />',
                    file_url,
                )
            # For non-image files, show a file icon and name
            return format_html(
                '<a href="{}" target="_blank">📁 {}</a>',
                file_url,
                file_name.split("/")[-1],
            )
        return "-"


@admin.register(Coach)
class CoachAdmin(ModelAdmin):
    """
    Admin interface for the Coach model.
    """

    list_display = (
        "first_name",
        "last_name",
        "user",
        "type",
        "category",
        "website",
        "email",
        "phone_number",
        "location",
        "street_no",
        "zip_code",
        "city",
        "country",
        "verification_status",
        "experience_level",
    )
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "first_name",
        "last_name",
        "type",
        "email",
        "phone_number",
        "location",
        "category__name",
        "subcategory__name",
    )
    list_filter = (
        "type",
        "verification_status",
        "experience_level",
        "category",
        "subcategory",
    )
    ordering = ("-id",)
    list_per_page = 20
    autocomplete_fields = ["user", "category", "subcategory"]
    readonly_fields = ("uuid", "created_at", "updated_at")
    inlines = [SocialMediaLinkInline, CoachMediaInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "title",
                    "first_name",
                    "last_name",
                    "profile_picture",
                    "cover_image",
                ),
            },
        ),
        (
            "Coach Details",
            {
                "fields": (
                    "review_status",
                    "about",
                    "type",
                    "category",
                    "subcategory",
                    "company",
                    "street_no",
                    "zip_code",
                    "city",
                    "country",
                    "website",
                    "email",
                    "phone_number",
                    "location",
                ),
            },
        ),
        (
            "Status Information",
            {
                "fields": (
                    "verification_status",
                    "experience_level",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    # TODO: add validation between coach category and subcategory


@admin.register(CoachMedia)
class CoachMediaAdmin(ModelAdmin):
    """
    Admin interface for the CoachMedia model.
    """

    list_display = (
        "id",
        "coach",
        "file_preview",
        "file_name",
        "created_at",
    )
    search_fields = (
        "coach__first_name",
        "coach__last_name",
        "file",
    )
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 20
    autocomplete_fields = ["coach"]
    readonly_fields = ("created_at", "file_preview")

    fieldsets = (
        (
            "Media Information",
            {
                "fields": (
                    "coach",
                    "file",
                    "file_preview",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at",),
            },
        ),
    )

    @admin.display(
        description="File Preview",
    )
    def file_preview(self, obj):
        """
        Display a preview of media file if it's an image, otherwise show the file name.
        """
        if obj.file:
            file_name = obj.file.name
            file_url = obj.file.url

            # Check if it's an image file
            image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
            if any(file_name.lower().endswith(ext) for ext in image_extensions):
                return format_html(
                    '<img src="{}" style="max-width: 100px; max-height: 100px; '
                    'object-fit: cover;" />',
                    file_url,
                )
            # For non-image files, show a file icon and name
            return format_html(
                '<a href="{}" target="_blank">📁 {}</a>',
                file_url,
                file_name.split("/")[-1],
            )
        return "-"

    @admin.display(
        description="File Name",
        ordering="file",
    )
    def file_name(self, obj):
        """
        Display just the filename without the full path.
        """
        if obj.file:
            return obj.file.name.split("/")[-1]
        return "-"


@admin.register(SocialMediaLink)
class SocialMediaLinkAdmin(ModelAdmin):
    """
    Admin interface for the SocialMediaLink model.
    """

    list_display = (
        "coach",
        "instagram",
        "facebook",
        "linkedin",
        "youtube",
        "tiktok",
        "x",
        "trustpilot",
        "google",
        "provexpert",
        "created_at",
    )
    search_fields = (
        "coach__first_name",
        "coach__last_name",
        "instagram",
        "facebook",
        "linkedin",
        "youtube",
        "tiktok",
        "x",
        "trustpilot",
        "google",
        "provexpert",
    )
    list_filter = ("created_at", "updated_at")
    ordering = ("-created_at",)
    list_per_page = 20
    autocomplete_fields = ["coach"]
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        (
            "Coach Information",
            {
                "fields": ("coach",),
            },
        ),
        (
            "Social Media Platforms",
            {
                "fields": (
                    "instagram",
                    "facebook",
                    "linkedin",
                    "youtube",
                    "tiktok",
                    "x",
                ),
            },
        ),
        (
            "Review Platforms",
            {
                "fields": (
                    "trustpilot",
                    "google",
                    "provexpert",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


@admin.register(SavedCoach)
class SavedCoachAdmin(ModelAdmin):
    """
    Admin interface for the SavedCoach model.
    """

    list_display = ("user", "coach", "uuid", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "coach__first_name",
        "coach__last_name",
    )
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 20
    autocomplete_fields = ["user", "coach"]
    readonly_fields = ("uuid", "created_at")


@admin.register(ClaimCoachRequest)
class ClaimCoachRequestAdmin(ModelAdmin):
    """
    Admin interface for the ClaimCoachRequest model.
    """

    list_display = (
        "first_name",
        "last_name",
        "user",
        "coach",
        "colored_status",
        "created_at",
    )
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "user__username",
        "user__email",
        "coach__first_name",
        "coach__last_name",
    )
    list_filter = ("status",)
    ordering = ("-created_at",)
    list_per_page = 20
    autocomplete_fields = ["user", "coach"]
    readonly_fields = ("uuid", "created_at")

    @admin.display(
        description="Status",
        ordering="status",
    )
    def colored_status(self, obj):
        """
        Display the status with improved styling:
        - Pending: Yellow
        - Approved: Green
        - Rejected: Red
        """
        styles = {
            ClaimCoachRequest.STATUS_PENDING: "background-color: #FFF3CD; color: #856404; padding: 3px 10px; border-radius: 4px; font-weight: 500; border: 1px solid #ffeeba;",  # Yellow  # noqa: E501
            ClaimCoachRequest.STATUS_APPROVED: "background-color: #D4EDDA; color: #155724; padding: 3px 10px; border-radius: 4px; font-weight: 500; border: 1px solid #c3e6cb;",  # Green  # noqa: E501
            ClaimCoachRequest.STATUS_REJECTED: "background-color: #F8D7DA; color: #721c24; padding: 3px 10px; border-radius: 4px; font-weight: 500; border: 1px solid #f5c6cb;",  # Red  # noqa: E501
        }

        return format_html(
            '<span style="{}">{}</span>',
            styles.get(obj.status, ""),
            obj.get_status_display(),
        )

    def has_change_permission(self, request, obj=None):
        """
        Determines if the user has permission to change the specified object.
        This method controls whether a user can modify a ClaimCoachRequest in the admin interface.
        It follows these rules:
        - Always allows access to the change list page (when obj is None)
        - Prevents editing requests that already have a coach with an associated user
        - Only allows editing requests that are in the 'PENDING' status
        Args:
            request: The current HttpRequest
            obj: The ClaimCoachRequest object being modified, or None for the change list
        Returns:
            bool: True if the user has permission to modify the object, False otherwise
        """  # noqa: E501

        if obj is None:
            return True

        current = type(obj).objects.get(pk=obj.pk)

        # Prevent updates if the coach is already having a user
        if current.coach and current.coach.user:
            return False

        return current.status == ClaimCoachRequest.STATUS_PENDING

    def has_delete_permission(self, request, obj=None):
        """
        Determine if the user has permission to delete the specified object.
        This method controls delete permissions for admin actions. It allows deletion
        only when the object is None (e.g., for model-level actions) or when the
        claim coach request is in a pending status.
        Args:
            request: The current HTTP request.
            obj: The object being checked for deletion permission. Can be None for
                 model-level checks.
        Returns:
            bool: True if the user has permission to delete the object, False otherwise.
                 Returns True if obj is None. For existing objects, returns True only if
                 the object's status is STATUS_PENDING.
        """

        if obj is None:
            return True

        current = type(obj).objects.get(pk=obj.pk)
        return current.status == ClaimCoachRequest.STATUS_PENDING


@admin.register(CoachReview)
class CoachReviewAdmin(ModelAdmin):
    """
    Admin interface for the CoachReview model.
    """

    list_display = (
        "first_name",
        "last_name",
        "coach",
        "rating",
        "colored_status",
        "created_at",
    )
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "comment",
        "coach__first_name",
        "coach__last_name",
        "user__username",
        "user__email",
    )
    list_filter = ("status", "rating", "date")
    ordering = ("-created_at",)
    list_per_page = 20
    autocomplete_fields = ["user", "coach"]
    readonly_fields = ("uuid", "created_at", "updated_at")

    @admin.display(
        description="Status",
        ordering="status",
    )
    def colored_status(self, obj):
        """
        Display the status with improved styling:
        - Pending: Yellow
        - Approved: Green
        - Rejected: Red
        """
        styles = {
            CoachReview.STATUS_PENDING: "background-color: #FFF3CD; color: #856404; padding: 3px 10px; border-radius: 4px; font-weight: 500; border: 1px solid #ffeeba;",  # Yellow  # noqa: E501
            CoachReview.STATUS_APPROVED: "background-color: #D4EDDA; color: #155724; padding: 3px 10px; border-radius: 4px; font-weight: 500; border: 1px solid #c3e6cb;",  # Green  # noqa: E501
            CoachReview.STATUS_REJECTED: "background-color: #F8D7DA; color: #721c24; padding: 3px 10px; border-radius: 4px; font-weight: 500; border: 1px solid #f5c6cb;",  # Red  # noqa: E501
        }

        return format_html(
            '<span style="{}">{}</span>',
            styles.get(obj.status, ""),
            obj.get_status_display(),
        )

    def has_change_permission(self, request, obj=None):
        """
        Determines if the user has permission to change the specified object.
        This method controls whether a user can modify a CoachReview in the
        admin interface. It follows these rules:
        - Always allows access to the change list page (when obj is None)
        - Only allows editing reviews that are in the 'PENDING' status

        Args:
            request: The current HttpRequest
            obj: The CoachReview object being modified, or None for the change list

        Returns:
            bool: True if the user has permission to modify the object, False otherwise
        """

        if obj is None:
            return True

        current = type(obj).objects.get(pk=obj.pk)
        return current.status == CoachReview.STATUS_PENDING

    def has_delete_permission(self, request, obj=None):
        """
        Determine if the user has permission to delete the specified object.
        This method controls delete permissions for admin actions. It allows deletion
        only when the object is None (e.g., for model-level actions) or when the
        coach review is in a pending status.

        Args:
            request: The current HTTP request.
            obj: The object being checked for deletion permission. Can be None for
                 model-level checks.

        Returns:
            bool: True if the user has permission to delete the object, False otherwise.
                 Returns True if obj is None. For existing objects, returns True only if
                 the object's status is STATUS_PENDING.
        """

        if obj is None:
            return True

        current = type(obj).objects.get(pk=obj.pk)
        return current.status == CoachReview.STATUS_PENDING


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """
    Admin interface for the Category model.
    """

    list_display = ("name", "description", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("created_at", "updated_at")
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        (
            "Category Information",
            {
                "fields": (
                    "icon",
                    "name",
                    "description",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(SubCategory)
class SubCategoryAdmin(ModelAdmin):
    """
    Admin interface for the SubCategory model.
    """

    list_display = ("category", "name", "description", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("created_at", "updated_at")
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        (
            "SubCategory Information",
            {
                "fields": (
                    "category",
                    "icon",
                    "name",
                    "description",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
