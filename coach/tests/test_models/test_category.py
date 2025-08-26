import pytest
from django.test import TestCase

from coach.models import Category
from coach.models import SubCategory
from coach.tests.factories import CategoryFactory
from coach.tests.factories import SubCategoryFactory


class TestCategory(TestCase):
    """Test cases for the Category model."""

    def setUp(self):
        """Set up test data."""
        self.category = CategoryFactory()

    def test_category_creation(self):
        """Test category creation with factory."""
        assert self.category.name is not None
        assert self.category.description is not None
        assert self.category.uuid is not None
        assert self.category.created_at is not None
        assert self.category.updated_at is not None

    def test_category_str_representation(self):
        """Test the string representation of category."""
        category = CategoryFactory(name="Life Coaching")
        assert str(category) == "Life Coaching"

    def test_category_name_uniqueness(self):
        """Test that factory uses get_or_create for category names."""
        # Create a category with a specific name
        category_name = "Unique Category Name"
        category1 = CategoryFactory(name=category_name)

        # Create another category with the same name - should return the same instance
        category2 = CategoryFactory(name=category_name)

        # Should be the same instance due to get_or_create
        assert category1.id == category2.id
        assert category1.name == category2.name
        assert Category.objects.filter(name=category_name).count() == 1

    def test_category_name_handling(self):
        """Test category name handling."""
        # Creating with valid name should work
        category = Category.objects.create(
            name="Valid Name",
            description="Test description",
        )
        assert category.name == "Valid Name"

        # Empty string is technically allowed by Django CharField
        empty_category = Category.objects.create(
            name="",
            description="Test description",
        )
        assert empty_category.name == ""

    def test_category_description_optional(self):
        """Test that category description is optional."""
        category = CategoryFactory(description="")
        category.save()
        category.refresh_from_db()
        assert category.description == ""

    def test_category_uuid_auto_generated(self):
        """Test that UUID is automatically generated."""
        category1 = CategoryFactory()
        category2 = CategoryFactory()

        # UUIDs should be different
        assert category1.uuid != category2.uuid
        # UUIDs should not be None
        assert category1.uuid is not None
        assert category2.uuid is not None

    def test_category_timestamps(self):
        """Test that timestamps are automatically set."""
        category = CategoryFactory()

        assert category.created_at is not None
        assert category.updated_at is not None

        # Update the category and check that updated_at changes
        original_updated_at = category.updated_at
        category.description = "Updated description"
        category.save()
        category.refresh_from_db()

        assert category.updated_at > original_updated_at

    def test_category_meta_options(self):
        """Test the model's meta options."""
        meta = Category._meta  # noqa: SLF001
        assert meta.verbose_name == "Category"
        assert meta.verbose_name_plural == "Categories"

    def test_category_with_long_name(self):
        """Test category with maximum length name."""
        long_name = "A" * 255  # Maximum CharField length
        category = CategoryFactory(name=long_name)
        category.save()
        category.refresh_from_db()
        assert category.name == long_name

    def test_category_with_long_description(self):
        """Test category with long description."""
        long_description = "This is a very long description. " * 100
        category = CategoryFactory(description=long_description)
        category.save()
        category.refresh_from_db()
        assert category.description == long_description

    def test_category_update(self):
        """Test updating category fields."""
        original_name = self.category.name
        original_description = self.category.description

        # Update fields
        self.category.name = "Updated Category Name"
        self.category.description = "Updated description"
        self.category.save()

        # Refresh from database
        self.category.refresh_from_db()

        # Verify updates
        assert self.category.name == "Updated Category Name"
        assert self.category.description == "Updated description"
        assert self.category.name != original_name
        assert self.category.description != original_description

    def test_category_deletion(self):
        """Test category deletion."""
        category_id = self.category.id
        self.category.delete()

        # Verify category is deleted
        with pytest.raises(Category.DoesNotExist):
            Category.objects.get(id=category_id)

    def test_category_ordering(self):
        """Test that categories can be ordered."""
        # Clear existing categories to ensure clean test
        Category.objects.all().delete()

        category1 = CategoryFactory(name="A Category")
        category2 = CategoryFactory(name="B Category")
        category3 = CategoryFactory(name="C Category")

        # Test ordering by name
        categories = Category.objects.order_by("name")
        assert list(categories) == [category1, category2, category3]

    def test_category_search_by_name(self):
        """Test searching categories by name."""
        CategoryFactory(name="Life Coaching")
        CategoryFactory(name="Business Coaching")
        CategoryFactory(name="Health Coaching")

        # Test case-insensitive search
        life_coaches = Category.objects.filter(name__icontains="life")
        assert life_coaches.count() == 1
        assert life_coaches.first().name == "Life Coaching"

    def test_category_search_by_description(self):
        """Test searching categories by description."""
        CategoryFactory(
            name="Category 1",
            description="This is about personal development",
        )
        CategoryFactory(
            name="Category 2",
            description="This is about business growth",
        )

        # Test description search
        personal_categories = Category.objects.filter(
            description__icontains="personal",
        )
        assert personal_categories.count() == 1
        assert "personal development" in personal_categories.first().description

    def test_category_subcategory_relationship(self):
        """Test the relationship between Category and SubCategory."""
        # Create a category and related subcategories
        category = CategoryFactory(name="Main Category")
        subcategory1 = SubCategoryFactory(category=category, name="Sub A")
        subcategory2 = SubCategoryFactory(category=category, name="Sub B")

        # Test relationship from category to subcategories
        assert category.subcategories.count() == 2  # noqa: PLR2004
        assert subcategory1 in category.subcategories.all()
        assert subcategory2 in category.subcategories.all()

        # Test relationship from subcategory to category
        assert subcategory1.category == category
        assert subcategory2.category == category

    def test_category_with_no_subcategories(self):
        """Test a category with no subcategories."""
        category = CategoryFactory(name="Empty Category")

        # Should have no subcategories initially
        assert category.subcategories.count() == 0

    def test_category_delete_cascade(self):
        """Test that deleting a category deletes associated subcategories."""
        # Create a category with subcategories
        category = CategoryFactory()
        subcategory1 = SubCategoryFactory(category=category)
        subcategory2 = SubCategoryFactory(category=category)

        subcategory1_id = subcategory1.id
        subcategory2_id = subcategory2.id

        # Delete the category
        category.delete()

        # Subcategories should be deleted (cascade)
        with pytest.raises(SubCategory.DoesNotExist):
            SubCategory.objects.get(id=subcategory1_id)
        with pytest.raises(SubCategory.DoesNotExist):
            SubCategory.objects.get(id=subcategory2_id)

    def test_reassign_subcategory_to_different_category(self):
        """Test reassigning a subcategory to a different category."""
        # Create categories and a subcategory
        category1 = CategoryFactory(name="Category 1")
        category2 = CategoryFactory(name="Category 2")
        subcategory = SubCategoryFactory(category=category1, name="Transferable Sub")

        # Check initial relationship
        assert subcategory.category == category1
        assert subcategory in category1.subcategories.all()

        # Reassign to category2
        subcategory.category = category2
        subcategory.save()
        subcategory.refresh_from_db()

        # Check updated relationship
        assert subcategory.category == category2
        assert subcategory in category2.subcategories.all()
        assert subcategory not in category1.subcategories.all()
