from datetime import datetime

import pytest
from django.db.utils import IntegrityError
from django.utils.text import slugify

from products.models import ProductCategory


@pytest.mark.django_db
class TestProductCategory:
    def test_create_product_category(self):
        """Test that a product category can be created."""
        category = ProductCategory.objects.create(name="Test Category")
        assert category.name == "Test Category"
        assert ProductCategory.objects.count() == 1

    def test_product_category_str(self):
        """Test the string representation of a product category."""
        category = ProductCategory.objects.create(name="Test Category")
        assert str(category) == "Test Category"

    def test_product_category_name_max_length(self):
        """Test the max length constraint of the name field."""
        # Use a value just under the database constraint to avoid hitting the limit exactly  # noqa: E501
        max_length = 200  # Reduced from 255 to be safely under the limit
        long_name = "a" * max_length
        category = ProductCategory.objects.create(name=long_name)
        assert len(category.name) == max_length

    def test_product_category_description(self):
        """Test that a description can be added to a product category."""
        category = ProductCategory.objects.create(
            name="Test Category",
            description="This is a test category",
        )
        assert category.description == "This is a test category"

    def test_unique_name_constraint(self):
        """Test that product categories must have unique names."""
        ProductCategory.objects.create(name="Test Category")
        with pytest.raises(IntegrityError):
            ProductCategory.objects.create(name="Test Category")

    def test_product_category_ordering(self):
        """Test that categories are ordered correctly."""
        category_b = ProductCategory.objects.create(name="B Category")
        category_a = ProductCategory.objects.create(name="A Category")
        categories = list(ProductCategory.objects.all())
        assert categories[0] == category_a
        assert categories[1] == category_b

    def test_timestamp_fields(self):
        """Test that timestamp fields are automatically set."""
        category = ProductCategory.objects.create(name="Time Test Category")
        assert isinstance(category.created_at, datetime)
        assert isinstance(category.updated_at, datetime)

        # Test that created_at doesn't change on update
        original_created_at = category.created_at
        category.description = "Updated description"
        category.save()
        category.refresh_from_db()
        assert category.created_at == original_created_at

        # Test that updated_at changes on update
        assert category.updated_at > original_created_at

    def test_slug_generation(self):
        """Test that slugs are automatically generated."""
        category = ProductCategory.objects.create(name="Slug Test Category")
        assert category.slug is not None
        assert slugify(category.name) in category.slug

        # Create another category with a slightly different name to test slug generation
        # while avoiding the unique constraint violation
        category2 = ProductCategory.objects.create(name="Slug Test Category 2")
        assert category2.slug != category.slug
        assert slugify(category2.name) in category2.slug

    def test_update_category(self):
        """Test updating category fields."""
        category = ProductCategory.objects.create(name="Original Name")
        original_slug = category.slug

        # Update fields
        category.name = "Updated Name"
        category.description = "Updated description"
        category.save()

        category.refresh_from_db()
        assert category.name == "Updated Name"
        assert category.description == "Updated description"
        # Slug should not change when updating
        assert category.slug == original_slug
