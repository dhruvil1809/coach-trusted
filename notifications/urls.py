from django.urls import path

from .views import NotificationListView
from .views import NotificationUpdateView

urlpatterns = [
    path("list/", NotificationListView.as_view(), name="list"),
    path("<int:id>/update/", NotificationUpdateView.as_view(), name="update"),
]

app_name = "notifications"
