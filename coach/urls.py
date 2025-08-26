from django.urls import path

from .views import CategoryListAPIView
from .views import ClaimCoachRequestCreateAPIView
from .views import CoachListAPIView
from .views import CoachRetrieveUpdateAPIView
from .views import CoachReviewCreateAPIView
from .views import CoachReviewListAPIView
from .views import CoachSocialMediaLinksRetrieveUpdateAPIView
from .views import CreateCoachAPIView
from .views import CreateSavedCoachAPIView
from .views import DeleteSavedCoachAPIView
from .views import SavedCoachListAPIView
from .views import SubCategoryListAPIView

app_name = "coach"
urlpatterns = [
    path("create/", CreateCoachAPIView.as_view(), name="create-coach"),
    path("categories/", CategoryListAPIView.as_view(), name="categories"),
    path("subcategories/", SubCategoryListAPIView.as_view(), name="subcategories"),
    path("saved/", SavedCoachListAPIView.as_view(), name="saved-coaches"),
    path("saved/add/", CreateSavedCoachAPIView.as_view(), name="create-saved-coach"),
    path(
        "saved/delete/<str:uuid>/",
        DeleteSavedCoachAPIView.as_view(),
        name="delete-saved-coach",
    ),
    path("claim/", ClaimCoachRequestCreateAPIView.as_view(), name="claim-coach"),
    path(
        "<str:coach_uuid>/reviews/",
        CoachReviewListAPIView.as_view(),
        name="list-reviews",
    ),
    path("reviews/add/", CoachReviewCreateAPIView.as_view(), name="create-review"),
    path(
        "<str:coach_uuid>/social-media/",
        CoachSocialMediaLinksRetrieveUpdateAPIView.as_view(),
        name="social-media-links",
    ),
    path("<str:uuid>/", CoachRetrieveUpdateAPIView.as_view(), name="retrieve-update"),
    path("", CoachListAPIView.as_view(), name="list"),
]
