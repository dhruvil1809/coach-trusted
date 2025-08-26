from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView

from . import ckeditor

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # Your stuff: custom urls includes go here
    path("auth/", include("authentication.urls", namespace="auth")),
    path("blogs/", include("blogs.urls", namespace="blogs")),
    path("coach/", include("coach.urls", namespace="coach")),
    path("events/", include("events.urls", namespace="events")),
    path("products/", include("products.urls", namespace="products")),
    path("inquiries/", include("inquiries.urls", namespace="inquiries")),
    path("notifications/", include("notifications.urls", namespace="notifications")),
    path("settings/", include("settings.urls", namespace="settings")),
    path("user/", include("core.users.urls", namespace="users")),
    path("quizzes/", include(("quizzes.urls", "quizzes"), namespace="quizzes")),
    # Media files
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("upload/", ckeditor.custom_upload_view, name="custom_upload_file"),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

# API URLS
urlpatterns += [
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
]

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
