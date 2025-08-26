from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Fields
from .models import Quiz


@admin.register(Quiz)
class QuizAdmin(ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "category",
        "fields",
        "journey",
        "created_at",
    )
    list_filter = ("category", "fields", "journey", "created_at")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("-created_at",)


@admin.register(Fields)
class FieldsAdmin(ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name", "description")
    ordering = ("name",)


# Register your models here.
