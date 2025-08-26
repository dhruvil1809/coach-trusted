from django.urls import path

from .views import CategoryListAPIView
from .views import PostDetailAPIView
from .views import PostListAPIView

app_name = "blogs"
urlpatterns = [
    path("categories/", CategoryListAPIView.as_view(), name="category-list"),
    path("posts/", PostListAPIView.as_view(), name="post-list"),
    path("posts/<slug:slug>/", PostDetailAPIView.as_view(), name="post-detail"),
]
