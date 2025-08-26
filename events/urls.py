from django.urls import path

from .views import EventListAPIView
from .views import EventRetrieveAPIView
from .views import RemoveSavedEventAPIView
from .views import SavedEventListCreateAPIView

app_name = "events"

urlpatterns = [
    path("", EventListAPIView.as_view(), name="list"),
    path("saved/", SavedEventListCreateAPIView.as_view(), name="saved"),
    path("saved/<uuid:uuid>/", RemoveSavedEventAPIView.as_view(), name="remove-saved"),
    path("<slug:slug>/", EventRetrieveAPIView.as_view(), name="detail"),
]
