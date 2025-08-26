from io import BytesIO

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from coach.models import Coach
from coach.tests.factories import CategoryFactory
from coach.tests.factories import SubCategoryFactory
from core.users.tests.factories import UserFactory


class TestCoach(TestCase):
    def setUp(self):
        self.user = UserFactory()

        # Create a coach using string type choices
        self.coach = Coach.objects.create(
            user=self.user,
            title="Head Coach",  # Add title
            first_name="Test",
            last_name="Coach",
            type=Coach.TYPE_OFFLINE,  # Use the constant from Coach model
        )

        # Create test image files
        self.profile_image = self._create_test_image("profile_test.jpg")
        self.cover_image = self._create_test_image("cover_test.png")

    def _create_test_image(self, filename, size=(100, 100), color="blue"):
        """Helper method to create a test image file"""
        image_file = BytesIO()
        image = Image.new("RGB", size, color)
        image.save(image_file, "JPEG" if filename.endswith(".jpg") else "PNG")
        image_file.seek(0)
        return SimpleUploadedFile(
            filename,
            image_file.read(),
            content_type="image/jpeg" if filename.endswith(".jpg") else "image/png",
        )

    def test_coach_creation(self):
        """Test that coach can be created with minimal required fields"""
        assert self.coach.title == "Head Coach"
        assert self.coach.first_name == "Test"
        assert self.coach.last_name == "Coach"
        assert self.coach.user == self.user
        assert self.coach.type == Coach.TYPE_OFFLINE
        assert self.coach.verification_status == "not verified"
        assert self.coach.experience_level == "beginner"
        # New fields should be blank by default
        assert self.coach.street_no == ""
        assert self.coach.zip_code == ""
        assert self.coach.city == ""
        assert self.coach.country == ""

    def test_string_representation(self):
        """Test string representation of coach model"""
        assert str(self.coach) == f"{self.coach.first_name} {self.coach.last_name}"

    def test_coach_with_all_fields(self):
        """Test coach creation with all fields"""
        coach = Coach.objects.create(
            user=UserFactory(),
            title="All Fields Coach",  # Add title
            first_name="Full",
            last_name="Coach",
            type=Coach.TYPE_ONLINE,  # Use constant instead of string literal
            website="https://coachtrusted.com",
            email="coach@example.com",
            phone_number="+1234567890",
            location="New York, NY",
            verification_status="verified",
            experience_level="expert",
            street_no="123A",
            zip_code="90210",
            city="Los Angeles",
            country="USA",
        )
        assert coach.title == "All Fields Coach"
        assert coach.website == "https://coachtrusted.com"
        assert coach.email == "coach@example.com"
        assert coach.phone_number == "+1234567890"
        assert coach.location == "New York, NY"
        assert coach.verification_status == "verified"
        assert coach.experience_level == "expert"
        assert coach.type == Coach.TYPE_ONLINE
        assert coach.street_no == "123A"
        assert coach.zip_code == "90210"
        assert coach.city == "Los Angeles"
        assert coach.country == "USA"

    def test_verification_status_choices(self):
        """Test verification status choices"""
        coach = Coach.objects.get(id=self.coach.id)
        coach.verification_status = "verified"
        coach.save()
        assert coach.verification_status == "verified"

        coach.verification_status = "verified plus"
        coach.save()
        assert coach.verification_status == "verified plus"

        # Default value
        assert self.coach.verification_status == "not verified"

    def test_experience_level_choices(self):
        """Test experience level choices"""
        coach = Coach.objects.get(id=self.coach.id)
        coach.experience_level = "intermediate"
        coach.save()
        assert coach.experience_level == "intermediate"

        coach.experience_level = "expert"
        coach.save()
        assert coach.experience_level == "expert"

        # Default value
        assert self.coach.experience_level == "beginner"

    def test_user_relationship(self):
        """Test relationship with User model"""
        assert hasattr(self.user, "coach")
        assert self.user.coach == self.coach

    def test_coach_type_choices(self):
        """Test coach type choices"""
        # Test setting type to online
        self.coach.type = Coach.TYPE_ONLINE
        self.coach.save()
        self.coach.refresh_from_db()
        assert self.coach.type == Coach.TYPE_ONLINE

        # Test setting type back to offline
        self.coach.type = Coach.TYPE_OFFLINE
        self.coach.save()
        self.coach.refresh_from_db()
        assert self.coach.type == Coach.TYPE_OFFLINE

    def test_coach_image_uploads(self):
        """Test coach image uploads and upload path functions"""
        # Test uploading profile picture
        self.coach.profile_picture = self.profile_image
        self.coach.save()

        # Test uploading cover image
        self.coach.cover_image = self.cover_image
        self.coach.save()

        # Refresh from database
        self.coach.refresh_from_db()

        # Verify images were saved
        assert self.coach.profile_picture is not None
        assert self.coach.cover_image is not None

    def test_uuid_generation(self):
        """Test UUID is automatically generated and unique"""
        assert self.coach.uuid is not None

        # Create another coach and verify UUID is different
        another_coach = Coach.objects.create(
            user=UserFactory(),
            first_name="Another",
            last_name="Coach",
            type=Coach.TYPE_OFFLINE,  # Use constant
        )
        assert self.coach.uuid != another_coach.uuid

    def test_update_coach_fields(self):
        """Test updating coach fields"""
        # Update fields
        self.coach.first_name = "Updated"
        self.coach.last_name = "Coach"
        self.coach.website = "https://updatedcoach.com"
        self.coach.email = "updated@example.com"
        self.coach.phone_number = "+9876543210"
        self.coach.location = "Updated Location"
        self.coach.save()

        # Refresh from database
        self.coach.refresh_from_db()

        # Verify fields were updated
        assert self.coach.first_name == "Updated"
        assert self.coach.last_name == "Coach"
        assert self.coach.website == "https://updatedcoach.com"
        assert self.coach.email == "updated@example.com"
        assert self.coach.phone_number == "+9876543210"
        assert self.coach.location == "Updated Location"

    def test_coach_field_validation(self):
        """Test field validation for Coach model"""
        # Test with invalid website format
        coach = Coach(
            user=UserFactory(),
            first_name="Invalid",
            last_name="Coach",
            type=Coach.TYPE_OFFLINE,  # Use constant
            website="invalid-website-format",
        )

        with pytest.raises(ValidationError):
            coach.full_clean()

    def test_coach_category_relationship(self):
        """Test category relationship with Coach model"""
        # Create a category
        category = CategoryFactory()

        # Assign category to coach
        self.coach.category = category
        self.coach.save()
        self.coach.refresh_from_db()

        # Verify relationship
        assert self.coach.category == category
        assert self.coach in Coach.objects.filter(category=category)

    def test_coach_subcategory_relationship(self):
        """Test subcategory many-to-many relationship with Coach model"""
        # Create subcategories
        subcategory1 = SubCategoryFactory()
        subcategory2 = SubCategoryFactory()
        subcategory3 = SubCategoryFactory()

        # Add subcategories to coach
        self.coach.subcategory.add(subcategory1, subcategory2)
        self.coach.save()

        # Verify relationships
        assert self.coach.subcategory.count() == 2  # noqa: PLR2004
        assert subcategory1 in self.coach.subcategory.all()
        assert subcategory2 in self.coach.subcategory.all()
        assert subcategory3 not in self.coach.subcategory.all()

        # Test removing subcategory
        self.coach.subcategory.remove(subcategory1)
        assert self.coach.subcategory.count() == 1
        assert subcategory1 not in self.coach.subcategory.all()
        assert subcategory2 in self.coach.subcategory.all()

    def test_coach_with_category_and_subcategories(self):
        """Test coach creation with category and subcategories"""
        category = CategoryFactory()
        subcategory1 = SubCategoryFactory()
        subcategory2 = SubCategoryFactory()

        # Create coach with category
        coach = Coach.objects.create(
            user=UserFactory(),
            title="Category Coach",  # Add title
            first_name="Category",
            last_name="Coach",
            type=Coach.TYPE_ONLINE,
            category=category,
        )

        # Add subcategories
        coach.subcategory.add(subcategory1, subcategory2)

        # Verify all relationships
        assert coach.category == category
        assert coach.subcategory.count() == 2  # noqa: PLR2004
        assert subcategory1 in coach.subcategory.all()
        assert subcategory2 in coach.subcategory.all()

    def test_coach_category_nullable(self):
        """Test that category field can be null"""
        coach = Coach.objects.create(
            user=UserFactory(),
            title="No Category Coach",  # Add title
            first_name="No Category",
            last_name="Coach",
            type=Coach.TYPE_OFFLINE,
            category=None,  # Explicitly set to None
        )

        assert coach.category is None

    def test_coach_subcategory_empty(self):
        """Test that subcategory field can be empty"""
        coach = Coach.objects.create(
            user=UserFactory(),
            title="No Subcategories Coach",  # Add title
            first_name="No Subcategories",
            last_name="Coach",
            type=Coach.TYPE_OFFLINE,
        )

        assert coach.subcategory.count() == 0
        assert list(coach.subcategory.all()) == []

    def test_category_cascade_behavior(self):
        """Test behavior when category is deleted (SET_NULL)"""
        category = CategoryFactory()
        self.coach.category = category
        self.coach.save()

        # Delete category
        category.delete()
        self.coach.refresh_from_db()

        # Coach should still exist but category should be None
        assert self.coach.category is None

    def test_subcategory_cascade_behavior(self):
        """Test behavior when subcategory is deleted"""
        subcategory1 = SubCategoryFactory()
        subcategory2 = SubCategoryFactory()

        self.coach.subcategory.add(subcategory1, subcategory2)
        initial_count = self.coach.subcategory.count()

        # Delete one subcategory
        subcategory1.delete()

        # Coach should still exist with one less subcategory
        assert self.coach.subcategory.count() == initial_count - 1
        assert subcategory1 not in self.coach.subcategory.all()
        assert subcategory2 in self.coach.subcategory.all()

    def test_coach_category_and_subcategory_relationships(self):
        """Test comprehensive category and subcategory relationships for a coach."""
        # Create categories and subcategories
        main_category = CategoryFactory(name="Main Category")
        other_category = CategoryFactory(name="Other Category")

        sub1 = SubCategoryFactory(category=main_category, name="Sub A")
        sub2 = SubCategoryFactory(category=main_category, name="Sub B")
        sub3 = SubCategoryFactory(category=other_category, name="Sub C")

        # Create coach with category and subcategories from different categories
        coach = Coach.objects.create(
            user=UserFactory(),
            title="Mixed Coach",  # Add title
            first_name="Mixed",
            last_name="Coach",
            category=main_category,
        )

        # Add subcategories from different parent categories
        coach.subcategory.add(sub1, sub2, sub3)

        # Verify relationships
        assert coach.category == main_category
        assert coach.subcategory.count() == 3  # noqa: PLR2004
        assert sub1 in coach.subcategory.all()
        assert sub2 in coach.subcategory.all()
        assert sub3 in coach.subcategory.all()

        # Test reverse relationships
        assert coach in main_category.coaches.all()
        assert coach in sub1.coaches.all()
        assert coach in sub2.coaches.all()
        assert coach in sub3.coaches.all()

    def test_change_coach_category(self):
        """Test changing a coach's category."""
        # Create categories
        category1 = CategoryFactory(name="Category 1")
        category2 = CategoryFactory(name="Category 2")

        # Create coach with category1
        coach = Coach.objects.create(
            user=UserFactory(),
            title="Changing Coach",  # Add title
            first_name="Changing",
            last_name="Coach",
            category=category1,
        )

        # Verify initial relationship
        assert coach.category == category1
        assert coach in category1.coaches.all()

        # Change to category2
        coach.category = category2
        coach.save()
        coach.refresh_from_db()

        # Verify updated relationship
        assert coach.category == category2
        assert coach in category2.coaches.all()
        assert coach not in category1.coaches.all()

    def test_category_and_subcategory_from_same_category(self):
        """Test subcategories from the same category as the coach's main category."""
        # Create category with subcategories
        category = CategoryFactory(name="Main Category")
        sub1 = SubCategoryFactory(category=category, name="Related Sub 1")
        sub2 = SubCategoryFactory(category=category, name="Related Sub 2")

        # Create coach with consistent category and subcategories
        coach = Coach.objects.create(
            user=UserFactory(),
            title="Consistent Coach",  # Add title
            first_name="Consistent",
            last_name="Coach",
            category=category,
        )
        coach.subcategory.add(sub1, sub2)

        # Verify relationships
        assert coach.category == category
        assert coach.subcategory.count() == 2  # noqa: PLR2004
        assert set(coach.subcategory.all()) == {sub1, sub2}

        # Verify all subcategories belong to coach's category
        for sub in coach.subcategory.all():
            assert sub.category == coach.category

    def test_coach_about_field(self):
        """Test the about field for Coach model."""
        # Set about field
        self.coach.about = "This is a test about section."
        self.coach.save()
        self.coach.refresh_from_db()
        assert self.coach.about == "This is a test about section."

        # Test about can be blank or None (if allowed by model)
        self.coach.about = ""
        self.coach.save()
        self.coach.refresh_from_db()
        assert self.coach.about == ""
