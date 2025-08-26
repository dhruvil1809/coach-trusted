from django.urls import path

from .views import MetaContentDetailView
from .views import MetaContentListView

urlpatterns = [
    path("meta-content/", MetaContentListView.as_view(), name="meta-content-list"),
    path(
        "meta-content/<int:pk>/",
        MetaContentDetailView.as_view(),
        name="meta-content-detail",
    ),
]

app_name = "settings"
