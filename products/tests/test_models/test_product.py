from datetime import date
from datetime import datetime
from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.text import slugify
from PIL import Image

from coach.models import Coach
from coach.tests.factories import CoachFactory
from products.models import Product
from products.tests.factories import ProductCategoryFactory
from products.tests.factories import ProductTypeFactory


class TestProduct(TestCase):
    def setUp(self):
        # Use coach type constant instead of CoachType model
        self.coach_type = Coach.TYPE_ONLINE

        # Create a coach for the product
        self.coach = CoachFactory(type=self.coach_type)

        # Create a category for the product
        self.category = ProductCategoryFactory(
            name="Test Category",
            description="Test category description",
        )

        # Create test image file
        self.product_image = self._create_test_image("product_test.jpg")

        # Create a product type for testing
        self.product_type = ProductTypeFactory(
            name="Course",
            description="Educational course content",
        )

        # Create a basic product
        self.product = Product.objects.create(
            coach=self.coach,
            name="Test Product",
            description="This is a test product",
            image=self.product_image,
            category=self.category,
            product_type=self.product_type,
            language="en",
            price=Decimal("99.99"),
            external_url="https://example.com/product",
            release_date=date(2024, 1, 15),
            ct_id="ct-123456",
            product_id="prod-789012",
        )

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

    def test_product_creation(self):
        """Test that product can be created with required fields"""
        assert self.product.name == "Test Product"
        assert self.product.description == "This is a test product"
        assert self.product.price == Decimal("99.99")
        assert self.product.language == "en"
        assert self.product.product_type == self.product_type
        assert self.product.coach == self.coach
        assert self.product.category == self.category
        assert self.product.image is not None
        assert self.product.external_url == "https://example.com/product"
        assert self.product.release_date == date(2024, 1, 15)
        assert self.product.ct_id == "ct-123456"
        assert self.product.product_id == "prod-789012"

    def test_string_representation(self):
        """Test string representation of product model"""
        assert str(self.product) == "Test Product"

    def test_uuid_generation(self):
        """Test that UUID is automatically generated"""
        assert self.product.uuid is not None
        # UUID should be unique for each product
        another_product = Product.objects.create(
            coach=self.coach,
            name="Another Product",
            description="Another test product",
            image=self._create_test_image("another_product.jpg"),
            category=self.category,
            price=Decimal("49.99"),
        )
        assert self.product.uuid != another_product.uuid

    def test_timestamp_fields(self):
        """Test timestamp fields"""
        assert isinstance(self.product.created_at, datetime)
        assert isinstance(self.product.updated_at, datetime)

        # Test that created_at doesn't change on update
        original_created_at = self.product.created_at
        self.product.name = "Updated Product Name"
        self.product.save()
        self.product.refresh_from_db()
        assert self.product.created_at == original_created_at

        # Test that updated_at changes on update
        assert self.product.updated_at > original_created_at

    def test_coach_relationship(self):
        """Test relationship with Coach model"""
        assert self.product.coach == self.coach

        # Test that products appear in the coach's related manager
        assert self.product in self.coach.products.all()

    def test_category_relationship(self):
        """Test relationship with ProductCategory model"""
        assert self.product.category == self.category

        # Test that products appear in the category's related manager
        assert self.product in self.category.products.all()

    def test_update_product(self):
        """Test updating product fields"""
        self.product.name = "Updated Product"
        self.product.description = "Updated description"
        self.product.price = Decimal("149.99")
        self.product.save()

        self.product.refresh_from_db()
        assert self.product.name == "Updated Product"
        assert self.product.description == "Updated description"
        assert self.product.price == Decimal("149.99")

    def test_slug_generation(self):
        """Test that slugs are automatically generated and unique"""
        # Check that slug was created automatically
        assert self.product.slug is not None

        # Check that slug contains the slugified version of the product name
        assert slugify(self.product.name) in self.product.slug

        # Create another product with the same name to test unique slugs
        same_name_product = Product.objects.create(
            coach=self.coach,
            name="Test Product",  # Same name as self.product
            description="Another product with the same name",
            image=self._create_test_image("duplicate_name.jpg"),
            category=self.category,
            price=Decimal("79.99"),
        )

        # Check that slugs are different even with the same name
        assert self.product.slug != same_name_product.slug

        # Test that slug doesn't change when updating other fields
        original_slug = self.product.slug
        self.product.price = Decimal("199.99")
        self.product.description = "Updated description without changing name"
        self.product.save()
        self.product.refresh_from_db()

        assert self.product.slug == original_slug

    def test_is_featured_field(self):
        """Test is_featured field functionality"""
        # Test default value
        assert self.product.is_featured is False

        # Test setting is_featured to True
        self.product.is_featured = True
        self.product.save()
        self.product.refresh_from_db()
        assert self.product.is_featured is True

        # Test setting is_featured to False
        self.product.is_featured = False
        self.product.save()
        self.product.refresh_from_db()
        assert self.product.is_featured is False

        # Test creating a product with is_featured=True
        featured_product = Product.objects.create(
            coach=self.coach,
            name="Featured Product",
            description="This is a featured product",
            image=self._create_test_image("featured_product.jpg"),
            category=self.category,
            price=Decimal("199.99"),
            is_featured=True,
        )
        assert featured_product.is_featured is True

    def test_language_field(self):
        """Test language field functionality"""
        # Test default value
        product_without_language = Product.objects.create(
            coach=self.coach,
            name="Product Without Language",
            description="Product created without specifying language",
            image=self._create_test_image("no_lang.jpg"),
            category=self.category,
            price=Decimal("50.00"),
        )
        assert product_without_language.language == "en"  # Default value

        # Test setting different language values
        language_choices = ["en", "es", "fr", "de", "it"]
        for lang in language_choices:
            product = Product.objects.create(
                coach=self.coach,
                name=f"Product {lang.upper()}",
                description=f"Product in {lang}",
                image=self._create_test_image(f"product_{lang}.jpg"),
                category=self.category,
                language=lang,
                price=Decimal("75.00"),
            )
            assert product.language == lang

        # Test updating language
        self.product.language = "es"
        self.product.save()
        self.product.refresh_from_db()
        assert self.product.language == "es"

    def test_product_type_relationship(self):
        """Test relationship with ProductType model"""
        assert self.product.product_type == self.product_type

        # Test that products appear in the product_type's related manager
        assert self.product in self.product_type.products.all()

        # Test product without product_type (nullable field)
        product_without_type = Product.objects.create(
            coach=self.coach,
            name="Product Without Type",
            description="Product without product type",
            image=self._create_test_image("no_type.jpg"),
            category=self.category,
            price=Decimal("25.00"),
        )
        assert product_without_type.product_type is None

        # Test updating product_type
        new_product_type = ProductTypeFactory(name="Workshop")
        self.product.product_type = new_product_type
        self.product.save()
        self.product.refresh_from_db()
        assert self.product.product_type == new_product_type

    def test_external_url_field(self):
        """Test external_url field functionality"""
        # Test that external_url is set correctly
        assert self.product.external_url == "https://example.com/product"

        # Test product without external_url (blank field)
        product_without_url = Product.objects.create(
            coach=self.coach,
            name="Product Without URL",
            description="Product without external URL",
            image=self._create_test_image("no_url.jpg"),
            category=self.category,
            price=Decimal("30.00"),
        )
        assert product_without_url.external_url == ""

        # Test updating external_url
        self.product.external_url = "https://updated-example.com/product"
        self.product.save()
        self.product.refresh_from_db()
        assert self.product.external_url == "https://updated-example.com/product"

        # Test setting external_url to empty string
        self.product.external_url = ""
        self.product.save()
        self.product.refresh_from_db()
        assert self.product.external_url == ""

    def test_release_date_field(self):
        """Test release_date field functionality"""
        # Test that release_date is set correctly
        assert self.product.release_date == date(2024, 1, 15)

        # Test product without release_date (nullable field)
        product_without_date = Product.objects.create(
            coach=self.coach,
            name="Product Without Date",
            description="Product without release date",
            image=self._create_test_image("no_date.jpg"),
            category=self.category,
            price=Decimal("40.00"),
        )
        assert product_without_date.release_date is None

        # Test updating release_date
        new_date = date(2024, 6, 30)
        self.product.release_date = new_date
        self.product.save()
        self.product.refresh_from_db()
        assert self.product.release_date == new_date

        # Test setting release_date to None
        self.product.release_date = None
        self.product.save()
        self.product.refresh_from_db()
        assert self.product.release_date is None

    def test_ct_id_field(self):
        """Test ct_id field functionality"""
        # Test that ct_id is set correctly
        assert self.product.ct_id == "ct-123456"

        # Test product without ct_id (nullable field)
        product_without_ct_id = Product.objects.create(
            coach=self.coach,
            name="Product Without CT ID",
            description="Product without CT ID",
            image=self._create_test_image("no_ct_id.jpg"),
            category=self.category,
            price=Decimal("35.00"),
        )
        assert product_without_ct_id.ct_id is None

        # Test updating ct_id
        self.product.ct_id = "ct-updated-789"
        self.product.save()
        self.product.refresh_from_db()
        assert self.product.ct_id == "ct-updated-789"

        # Test setting ct_id to None
        self.product.ct_id = None
        self.product.save()
        self.product.refresh_from_db()
        assert self.product.ct_id is None

        # Test ct_id uniqueness
        import pytest
        from django.db import IntegrityError

        # First set a unique ct_id
        self.product.ct_id = "ct-unique-123"
        self.product.save()

        # Create another product with the same ct_id should fail
        with pytest.raises(IntegrityError):
            Product.objects.create(
                coach=self.coach,
                name="Duplicate CT ID Product",
                description="Product with duplicate CT ID",
                image=self._create_test_image("duplicate_ct.jpg"),
                category=self.category,
                price=Decimal("45.00"),
                ct_id="ct-unique-123",  # Same ct_id as self.product
            )

    def test_product_id_field(self):
        """Test product_id field functionality"""
        # Test that product_id is set correctly
        assert self.product.product_id == "prod-789012"

        # Test product without product_id (nullable field)
        product_without_product_id = Product.objects.create(
            coach=self.coach,
            name="Product Without Product ID",
            description="Product without product ID",
            image=self._create_test_image("no_prod_id.jpg"),
            category=self.category,
            price=Decimal("55.00"),
        )
        assert product_without_product_id.product_id is None

        # Test updating product_id
        self.product.product_id = "prod-updated-456"
        self.product.save()
        self.product.refresh_from_db()
        assert self.product.product_id == "prod-updated-456"

        # Test setting product_id to None
        self.product.product_id = None
        self.product.save()
        self.product.refresh_from_db()
        assert self.product.product_id is None

        # Test product_id uniqueness
        import pytest
        from django.db import IntegrityError

        # First set a unique product_id
        self.product.product_id = "prod-unique-456"
        self.product.save()

        # Create another product with the same product_id should fail
        with pytest.raises(IntegrityError):
            Product.objects.create(
                coach=self.coach,
                name="Duplicate Product ID Product",
                description="Product with duplicate product ID",
                image=self._create_test_image("duplicate_prod.jpg"),
                category=self.category,
                price=Decimal("65.00"),
                product_id="prod-unique-456",  # Same product_id as self.product
            )
