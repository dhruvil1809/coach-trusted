from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import PasswordResetToken
from .models import Profile
from .models import User
from .models import VerificationCode

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "first_name", "last_name", "is_superuser"]
    search_fields = ["first_name", "last_name", "email", "username"]


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = [
        "user",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "is_user_active",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "user__username",
        "first_name",
        "last_name",
        "email",
        "phone_number",
    ]
    autocomplete_fields = ["user"]
    readonly_fields = ["created_at", "updated_at", "is_user_active"]
    fieldsets = (
        (None, {"fields": ("user", "is_user_active")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "profile_picture",
                    "first_name",
                    "last_name",
                    "email",
                    ("country_code"),
                    "phone_number",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(
        boolean=True,
    )
    def is_user_active(self, obj):
        """Check if the user is active."""
        return obj.user.is_active


@admin.register(VerificationCode)
class VerificationCodeAdmin(ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user")

    list_display = ["user", "code", "created_at", "is_valid"]
    readonly_fields = ["user", "created_at", "code", "is_valid"]
    search_fields = ["user__username", "code"]


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user")

    list_display = ["user", "token_display", "created_at", "is_valid"]
    readonly_fields = ["user", "created_at", "token", "is_valid"]
    search_fields = ["user__username", "user__email", "token"]
    list_filter = ["created_at"]
    ordering = ["-created_at"]

    @admin.display(description="Token")
    def token_display(self, obj):
        """Display first 10 characters of token for security."""
        return f"{obj.token[:10]}..." if obj.token else ""

    @admin.display(boolean=True, description="Valid")
    def is_valid(self, obj):
        """Check if the password reset token is still valid."""
        return obj.is_valid()
