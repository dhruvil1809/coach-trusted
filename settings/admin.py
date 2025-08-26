from django.contrib import admin
from unfold.admin import ModelAdmin

from settings.models import MetaContent


@admin.register(MetaContent)
class MetaContentAdmin(ModelAdmin):
    """
    Admin interface for the MetaContent model.
    """

    list_display = (
        "web_page",
        "meta_title",
        "meta_description",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "web_page",
        "meta_title",
        "meta_description",
    )
    list_filter = ("created_at", "updated_at")
    ordering = ("web_page",)
    list_per_page = 20
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Page Information",
            {
                "fields": ("web_page",),
            },
        ),
        (
            "Meta Tags",
            {
                "fields": (
                    "meta_title",
                    "meta_description",
                    "link_canonical",
                ),
            },
        ),
        (
            "SEO Content",
            {
                "fields": (
                    "schema",
                    "site_map",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
