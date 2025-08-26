from io import BytesIO
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from coach.models import Coach
from products.models import ProductMedia
from products.tests.factories import ProductFactory


class TestProductMedia(TestCase):
    def setUp(self):
        """Set up test data."""
        # Use coach type constant instead of CoachType model
        self.coach_type = Coach.TYPE_ONLINE

        # Pass coach type to ProductFactory
        self.product = ProductFactory(coach__type=self.coach_type)
        self.test_file = self._create_test_file("test_media.pdf")

    def _create_test_file(self, filename, content=b"test content"):
        """Helper method to create a test file."""
        return SimpleUploadedFile(
            name=filename,
            content=content,
            content_type="application/pdf",
        )

    def _create_test_image(
        self,
        filename="media_test.jpg",
        size=(100, 100),
        color="blue",
    ):
        """Helper method to create a test image file."""
        image_file = BytesIO()
        image = Image.new("RGB", size=size, color=color)
        image.save(image_file, "JPEG")
        image_file.seek(0)

        return SimpleUploadedFile(
            name=filename,
            content=image_file.read(),
            content_type="image/jpeg",
        )

    def test_product_media_creation(self):
        """Test creating a new product media."""
        media = ProductMedia.objects.create(
            product=self.product,
            media_file=self.test_file,
        )

        assert media.product == self.product
        assert media.media_file is not None
        assert media.created_at is not None

    def test_string_representation(self):
        """Test string representation of product media."""
        media = ProductMedia.objects.create(
            product=self.product,
            media_file=self.test_file,
        )

        expected_str = f"{self.product.name} - {media.media_file.name}"
        assert str(media) == expected_str

    def test_upload_path(self):
        """Test that media files are uploaded to the correct path."""
        media = ProductMedia.objects.create(
            product=self.product,
            media_file=self.test_file,
        )

        # Check that the file path includes 'products/media/'
        assert "products/media/" in media.media_file.path

    def test_upload_image(self):
        """Test uploading an image file."""
        image_file = self._create_test_image()
        media = ProductMedia.objects.create(product=self.product, media_file=image_file)

        assert media.media_file is not None
        assert Path(media.media_file.path).exists()
        assert Path(media.media_file.path).exists()

    def test_delete_media_file_on_delete(self):
        media = ProductMedia.objects.create(
            product=self.product,
            media_file=self.test_file,
        )

        file_path = media.media_file.path
        assert Path(file_path).exists()
        assert Path(file_path).exists()

        media.delete()

        # Check that the file has been deleted from storage
        assert not Path(file_path).exists()
        assert not Path(file_path).exists()

    def test_product_relation(self):
        """Test the relationship with Product model."""
        media1 = ProductMedia.objects.create(
            product=self.product,
            media_file=self._create_test_file("file1.pdf"),
        )

        media2 = ProductMedia.objects.create(
            product=self.product,
            media_file=self._create_test_file("file2.pdf"),
        )

        # Check that the product has all media files
        product_media = self.product.media.all()
        assert product_media.count() == 2  # noqa: PLR2004
        assert media1 in product_media
        assert media2 in product_media
