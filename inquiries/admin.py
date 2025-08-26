from django.contrib import admin
from unfold.admin import ModelAdmin

from inquiries.models import GeneralInquiry


@admin.register(GeneralInquiry)
class GeneralInquiryAdmin(ModelAdmin):
    """
    Admin interface for the GeneralInquiry model.
    """

    list_display = (
        "subject",
        "business_name",
        "first_name",
        "last_name",
        "email",
        "country",
        "created_at",
    )
    search_fields = (
        "subject",
        "business_name",
        "first_name",
        "last_name",
        "email",
        "message",
    )
    list_filter = ("country", "created_at")
    readonly_fields = ("created_at",)
    fieldsets = (
        (
            "Inquiry Details",
            {
                "fields": ("subject", "message"),
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "business_name",
                    "first_name",
                    "last_name",
                    "email",
                    "country",
                    "phone",
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
    date_hierarchy = "created_at"
