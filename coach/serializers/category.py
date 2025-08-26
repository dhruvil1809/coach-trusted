from rest_framework import serializers

from coach.models import Category
from coach.models import SubCategory


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """

    class Meta:
        model = Category
        fields = ["id", "uuid", "icon", "name"]


class SubCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the SubCategory model.
    """

    category = CategorySerializer(read_only=True)
    total_coach = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = ["id", "uuid", "icon", "name", "total_coach", "category"]

    def get_total_coach(self, obj):
        """
        Returns the total number of coaches in the subcategory.
        """
        return obj.coaches.count() if hasattr(obj, "coaches") else 0


class SubCategorySerializerWithoutCategory(serializers.ModelSerializer):
    """
    Serializer for the SubCategory model without category details.
    """

    class Meta:
        model = SubCategory
        fields = ["id", "uuid", "icon", "name"]
        read_only_fields = ["id", "uuid", "icon", "name"]


class CategoryWithSubCategoriesSerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model with nested SubCategories.
    """

    subcategories = SubCategorySerializerWithoutCategory(many=True, read_only=True)
    total_coach = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "uuid", "icon", "name", "total_coach", "subcategories"]
        read_only_fields = ["subcategories"]

    def get_total_coach(self, obj):
        """
        Returns the total number of coaches in the category.
        """
        return obj.coaches.count() if hasattr(obj, "coaches") else 0
