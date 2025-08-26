import html

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from blogs.models import Category
from blogs.models import Post


class CategoryListSerializer(ModelSerializer):
    post_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "post_count"]
        read_only_fields = ["id"]


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]
        read_only_fields = ["id"]


class PostListSerializer(ModelSerializer):
    category = CategorySerializer(read_only=True)
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "image",
            "excerpt",
            "category",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_excerpt(self, obj):
        """
        Return a shortened excerpt of the content (first 150 characters).
        """
        excerpt_length = 150
        content = obj.content
        if content:
            # Remove HTML tags and get plain text
            import re

            clean_content = re.sub(r"<[^>]+>", "", content)
            # Unescape HTML entities
            clean_content = html.unescape(clean_content)
            # Get first 150 characters and add ellipsis if needed
            if len(clean_content) > excerpt_length:
                return clean_content[:excerpt_length].strip() + "..."
            return clean_content.strip()
        return ""


class PostDetailSerializer(ModelSerializer):
    category = CategorySerializer(read_only=True)
    content = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "image",
            "content",
            "category",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_content(self, obj):
        """
        Return the content with HTML entities unescaped.
        """
        content = obj.content
        if content:
            return html.unescape(content)
        return content
