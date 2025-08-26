from django.urls import path

from .views import ProductListCreateAPIView
from .views import ProductMediaUpdateAPIView
from .views import ProductRetrieveUpdateAPIView
from .views import RemoveSavedProductAPIView
from .views import SavedProductListCreateAPIView

urlpatterns = [
    path("saved/", SavedProductListCreateAPIView.as_view(), name="saved"),
    path(
        "saved/<uuid:uuid>/",
        RemoveSavedProductAPIView.as_view(),
        name="remove-saved",
    ),
    path(
        "<slug:slug>/",
        ProductRetrieveUpdateAPIView.as_view(),
        name="retrieve-update",
    ),
    path(
        "<slug:slug>/media/",
        ProductMediaUpdateAPIView.as_view(),
        name="product-media",
    ),
    path("", ProductListCreateAPIView.as_view(), name="list-create"),
]

app_name = "products"
