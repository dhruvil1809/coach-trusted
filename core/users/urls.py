from django.urls import path

from .views import RetrieveUpdateProfileAPIView

app_name = "users"
urlpatterns = [
    path("profile/", RetrieveUpdateProfileAPIView.as_view(), name="profile"),
]
