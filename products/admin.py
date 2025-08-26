from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline

from products.models import Product
from products.models import ProductCategory
from products.models import ProductMedia
from products.models import ProductType
from products.models import SavedProduct


class ProductMediaInline(TabularInline):
    """
    Inline admin for ProductMedia to be used within ProductAdmin.
    """

    model = ProductMedia
    extra = 1  # Number of empty forms to display


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    """
    Admin interface for the Product model.
    """

    list_display = (
        "name",
        "coach",
        "category",
        "product_type",
        "language",
        "price",
        "is_featured",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "description",
        "coach__first_name",
        "coach__last_name",
        "category__name",
    )
    list_filter = ("category", "product_type", "language", "is_featured", "created_at")
    autocomplete_fields = ["coach", "category", "product_type"]
    readonly_fields = ("uuid", "slug", "created_at", "updated_at")
    inlines = [ProductMediaInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "coach",
                    "name",
                    "release_date",
                    "description",
                    "image",
                    "category",
                    "product_type",
                    "language",
                    "price",
                    "external_url",
                    "is_featured",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "uuid",
                    "slug",
                    "ct_id",
                    "product_id",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


@admin.register(ProductMedia)
class ProductMediaAdmin(ModelAdmin):
    """
    Admin interface for the ProductMedia model.
    """

    list_display = ("product", "media_file", "created_at")
    search_fields = ("product__name",)
    list_filter = ("created_at",)
    autocomplete_fields = ["product"]
    readonly_fields = ("created_at",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "product",
                    "media_file",
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


@admin.register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    """
    Admin interface for the ProductCategory model.
    """

    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("slug", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "slug",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


@admin.register(SavedProduct)
class SavedProductAdmin(ModelAdmin):
    """
    Admin interface for the SavedProduct model.
    """

    list_display = ("user", "product", "created_at", "uuid")
    search_fields = ("user__username", "product__name")
    list_filter = ("created_at",)
    autocomplete_fields = ["user", "product"]
    readonly_fields = ("created_at", "uuid")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "product",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "uuid"),
            },
        ),
    )


@admin.register(ProductType)
class ProductTypeAdmin(ModelAdmin):
    """
    Admin interface for the ProductType model.
    """

    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("created_at",)
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
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
            },
        ),
    )
