from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from blogs.models import Category
from blogs.models import Post


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "posts_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

    @display(description="Posts Count")
    def posts_count(self, obj):
        return obj.posts.count()

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            from django.utils.text import slugify

            obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ("title", "category", "status", "created_at", "updated_at")
    list_filter = ("status", "category", "created_at", "updated_at")
    search_fields = ("title", "content")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at", "slug")
    list_per_page = 20
    list_display_links = ("title",)
    list_editable = ("status",)

    fieldsets = (
        (
            None,
            {
                "fields": ("title", "slug", "category", "status"),
            },
        ),
        (
            "Content",
            {
                "fields": ("image", "content"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category")
