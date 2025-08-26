import pytest
from django.test import TestCase

from coach.models import SubCategory
from coach.tests.factories import CategoryFactory
from coach.tests.factories import SubCategoryFactory


class TestSubCategory(TestCase):
    """Test cases for the SubCategory model."""

    def setUp(self):
        """Set up test data."""
        self.subcategory = SubCategoryFactory()

    def test_subcategory_creation(self):
        """Test subcategory creation with factory."""
        assert self.subcategory.name is not None
        assert self.subcategory.description is not None
        assert self.subcategory.uuid is not None
        assert self.subcategory.created_at is not None
        assert self.subcategory.updated_at is not None

    def test_subcategory_str_representation(self):
        """Test the string representation of subcategory."""
        subcategory = SubCategoryFactory(name="Career Coaching")
        assert str(subcategory) == "Career Coaching"

    def test_subcategory_name_uniqueness(self):
        """Test that factory uses get_or_create for subcategory names."""
        # Create a subcategory with a specific name
        subcategory_name = "Unique SubCategory Name"
        subcategory1 = SubCategoryFactory(name=subcategory_name)

        # Create another subcategory with the same name - should return same instance
        subcategory2 = SubCategoryFactory(name=subcategory_name)

        # Should be the same instance due to get_or_create
        assert subcategory1.id == subcategory2.id
        assert subcategory1.name == subcategory2.name
        assert SubCategory.objects.filter(name=subcategory_name).count() == 1

    def test_subcategory_name_handling(self):
        """Test subcategory name handling."""
        # Creating with valid name should work
        subcategory = SubCategory.objects.create(
            name="Valid Name",
            description="Test description",
        )
        assert subcategory.name == "Valid Name"

        # Empty string is technically allowed by Django CharField
        empty_subcategory = SubCategory.objects.create(
            name="",
            description="Test description",
        )
        assert empty_subcategory.name == ""

    def test_subcategory_description_optional(self):
        """Test that subcategory description is optional."""
        subcategory = SubCategoryFactory(description="")
        subcategory.save()
        subcategory.refresh_from_db()
        assert subcategory.description == ""

    def test_subcategory_uuid_auto_generated(self):
        """Test that UUID is automatically generated."""
        subcategory1 = SubCategoryFactory()
        subcategory2 = SubCategoryFactory()

        # UUIDs should be different
        assert subcategory1.uuid != subcategory2.uuid
        # UUIDs should not be None
        assert subcategory1.uuid is not None
        assert subcategory2.uuid is not None

    def test_subcategory_timestamps(self):
        """Test that timestamps are automatically set."""
        subcategory = SubCategoryFactory()

        assert subcategory.created_at is not None
        assert subcategory.updated_at is not None

        # Update the subcategory and check that updated_at changes
        original_updated_at = subcategory.updated_at
        subcategory.description = "Updated description"
        subcategory.save()
        subcategory.refresh_from_db()

        assert subcategory.updated_at > original_updated_at

    def test_subcategory_meta_options(self):
        """Test the model's meta options."""
        meta = SubCategory._meta  # noqa: SLF001
        assert meta.verbose_name == "SubCategory"
        assert meta.verbose_name_plural == "SubCategories"

    def test_subcategory_with_long_name(self):
        """Test subcategory with maximum length name."""
        long_name = "A" * 255  # Maximum CharField length
        subcategory = SubCategoryFactory(name=long_name)
        subcategory.save()
        subcategory.refresh_from_db()
        assert subcategory.name == long_name

    def test_subcategory_with_long_description(self):
        """Test subcategory with long description."""
        long_description = "This is a very long description. " * 100
        subcategory = SubCategoryFactory(description=long_description)
        subcategory.save()
        subcategory.refresh_from_db()
        assert subcategory.description == long_description

    def test_subcategory_update(self):
        """Test updating subcategory fields."""
        original_name = self.subcategory.name
        original_description = self.subcategory.description

        # Update fields
        self.subcategory.name = "Updated SubCategory Name"
        self.subcategory.description = "Updated description"
        self.subcategory.save()

        # Refresh from database
        self.subcategory.refresh_from_db()

        # Verify updates
        assert self.subcategory.name == "Updated SubCategory Name"
        assert self.subcategory.description == "Updated description"
        assert self.subcategory.name != original_name
        assert self.subcategory.description != original_description

    def test_subcategory_deletion(self):
        """Test subcategory deletion."""
        subcategory_id = self.subcategory.id
        self.subcategory.delete()

        # Verify subcategory is deleted
        with pytest.raises(SubCategory.DoesNotExist):
            SubCategory.objects.get(id=subcategory_id)

    def test_subcategory_ordering(self):
        """Test that subcategories can be ordered."""
        # Clear existing subcategories to ensure clean test
        SubCategory.objects.all().delete()

        subcategory1 = SubCategoryFactory(name="A SubCategory")
        subcategory2 = SubCategoryFactory(name="B SubCategory")
        subcategory3 = SubCategoryFactory(name="C SubCategory")

        # Test ordering by name
        subcategories = SubCategory.objects.order_by("name")
        assert list(subcategories) == [subcategory1, subcategory2, subcategory3]

    def test_subcategory_search_by_name(self):
        """Test searching subcategories by name."""
        SubCategoryFactory(name="Career Development")
        SubCategoryFactory(name="Leadership Training")
        SubCategoryFactory(name="Personal Growth")

        # Test case-insensitive search
        career_subcategories = SubCategory.objects.filter(name__icontains="career")
        assert career_subcategories.count() == 1
        assert career_subcategories.first().name == "Career Development"

    def test_subcategory_search_by_description(self):
        """Test searching subcategories by description."""
        SubCategoryFactory(
            name="SubCategory 1",
            description="This focuses on individual skill development",
        )
        SubCategoryFactory(
            name="SubCategory 2",
            description="This focuses on team management",
        )

        # Test description search
        individual_subcategories = SubCategory.objects.filter(
            description__icontains="individual",
        )
        assert individual_subcategories.count() == 1
        assert "individual skill" in individual_subcategories.first().description

    def test_multiple_subcategories_creation(self):
        """Test creating multiple subcategories."""
        num_subcategories = 5
        subcategories = [
            SubCategoryFactory(name=f"SubCategory {i}")
            for i in range(num_subcategories)
        ]

        assert len(subcategories) == num_subcategories
        assert (
            SubCategory.objects.count() >= num_subcategories
        )  # Including setUp subcategory

        # All should have unique names
        names = [sc.name for sc in subcategories]
        assert len(names) == len(set(names))

    def test_subcategory_filtering(self):
        """Test filtering subcategories."""
        # Create subcategories with specific descriptions
        SubCategoryFactory(name="Test 1", description="fitness related content")
        SubCategoryFactory(name="Test 2", description="nutrition related content")
        SubCategoryFactory(name="Test 3", description="mental health content")

        # Filter by description content
        fitness_subcategories = SubCategory.objects.filter(
            description__icontains="fitness",
        )
        nutrition_subcategories = SubCategory.objects.filter(
            description__icontains="nutrition",
        )

        assert fitness_subcategories.count() == 1
        assert nutrition_subcategories.count() == 1
        assert fitness_subcategories.first().name == "Test 1"
        assert nutrition_subcategories.first().name == "Test 2"

    def test_subcategory_with_category(self):
        """Test subcategory with assigned category."""
        # Create a specific category
        category = CategoryFactory(name="Specialized Category")

        # Create subcategory with that category
        subcategory = SubCategoryFactory(category=category)

        # Verify relationship
        assert subcategory.category == category
        assert subcategory in category.subcategories.all()

    def test_subcategory_without_category(self):
        """Test subcategory without a category."""
        subcategory = SubCategoryFactory(category=None)
        assert subcategory.category is None

    def test_category_cascade_behavior(self):
        """Test behavior when parent category is deleted."""
        # Create category and subcategory
        category = CategoryFactory()
        subcategory = SubCategoryFactory(category=category)
        subcategory_id = subcategory.id

        # Delete the category
        category.delete()

        # The subcategory should be deleted as well (CASCADE)
        with pytest.raises(SubCategory.DoesNotExist):
            SubCategory.objects.get(id=subcategory_id)

    def test_multiple_subcategories_same_category(self):
        """Test multiple subcategories assigned to the same category."""
        category = CategoryFactory(name="Parent Category")

        # Create multiple subcategories for the same category
        subcategory1 = SubCategoryFactory(category=category, name="Sub A")
        subcategory2 = SubCategoryFactory(category=category, name="Sub B")
        subcategory3 = SubCategoryFactory(category=category, name="Sub C")

        # Verify relationships
        assert subcategory1.category == category
        assert subcategory2.category == category
        assert subcategory3.category == category

        # Check from the category perspective
        subcategories = category.subcategories.all()
        assert subcategory1 in subcategories
        assert subcategory2 in subcategories
        assert subcategory3 in subcategories
        assert category.subcategories.count() == 3  # noqa: PLR2004
