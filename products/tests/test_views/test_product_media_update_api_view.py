import json
from io import BytesIO
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from coach.models import Coach
from coach.tests.factories import CoachFactory
from core.users.models import User
from products.models import ProductMedia
from products.tests.factories import ProductCategoryFactory
from products.tests.factories import ProductFactory
from products.tests.factories import create_test_image


@pytest.mark.django_db
class ProductMediaUpdateAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Set up the coach type
        self.coach_type = Coach.TYPE_ONLINE

        # Create users
        self.user1 = User.objects.create_user(
            username="mediacoach",
            email="mediacoach@example.com",
            password="StrongPassword123",  # noqa: S106
            is_active=True,
        )

        self.user2 = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="StrongPassword123",  # noqa: S106
            is_active=True,
        )

        # Create coaches
        self.coach1 = CoachFactory(
            user=self.user1,
            first_name="Media Test",
            last_name="Coach",
            type=self.coach_type,
            website="https://mediatestcoach.com",
            email="mediatestcoach@example.com",
        )

        self.coach2 = CoachFactory(
            user=self.user2,
            first_name="Other",
            last_name="Coach",
            type=self.coach_type,
            website="https://othercoach.com",
            email="othercoach@example.com",
        )

        # Create product category
        self.category = ProductCategoryFactory(
            name="Media Test Category",
            description="Category for media testing",
        )

        # Create a product
        self.product = ProductFactory(
            name="Media Test Product",
            description="This is a product for media tests",
            price="99.99",
            coach=self.coach1,
            category=self.category,
            image=create_test_image("product_main.jpg"),
        )

        # Create some initial media for the product
        self.media1 = ProductMedia.objects.create(
            product=self.product,
            media_file=self._create_test_file("existing_file1.pdf"),
        )

        self.media2 = ProductMedia.objects.create(
            product=self.product,
            media_file=self._create_test_file("existing_file2.pdf"),
        )

        # URL for product media
        self.media_url = reverse(
            "products:product-media",
            kwargs={"slug": self.product.slug},
        )

    def _create_test_file(self, filename="test.pdf", content=b"test content"):
        """Helper method to create a test file."""
        return SimpleUploadedFile(
            name=filename,
            content=content,
            content_type="application/pdf",
        )

    def _create_test_image(self, filename="test.jpg", size=(100, 100), color="blue"):
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

    def test_retrieve_media_success(self):
        """Test successful retrieval of product media (no auth required)"""
        response = self.client.get(self.media_url)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data) == 2  # Two initial media files  # noqa: PLR2004

        # Check that media files have expected fields
        assert "id" in data[0]
        assert "media_file" in data[0]
        assert "created_at" in data[0]

    def test_retrieve_nonexistent_product_media(self):
        """Test 404 response when trying to retrieve media for non-existent product"""
        non_existent_url = reverse(
            "products:product-media",
            kwargs={"slug": "non-existent-slug"},
        )
        response = self.client.get(non_existent_url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_media_unauthenticated(self):
        """Test adding media without authentication fails"""
        test_file = self._create_test_file("new_file.pdf")

        # Prepare form data for the POST request
        form_data = {
            "media_files": [test_file],
        }

        response = self.client.post(
            self.media_url,
            data=form_data,
            format="multipart",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Verify no new media was added
        assert self.product.media.count() == 2  # noqa: PLR2004

    def test_add_media_wrong_user(self):
        """Test adding media by a different coach fails"""
        # Login as a different user (not the product owner)
        self.client.login(
            username="otheruser",
            password="StrongPassword123",  # noqa: S106
        )

        test_file = self._create_test_file("wrong_user_file.pdf")

        # Prepare form data for the POST request
        form_data = {
            "media_files": [test_file],
        }

        response = self.client.post(
            self.media_url,
            data=form_data,
            format="multipart",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Verify no new media was added
        assert self.product.media.count() == 2  # noqa: PLR2004

    def test_add_media_success(self):
        """Test successful addition of media files by product owner"""
        # Login as the product owner
        self.client.login(
            username="mediacoach",
            password="StrongPassword123",  # noqa: S106
        )

        test_file1 = self._create_test_file("new_file1.pdf")
        test_file2 = self._create_test_image("new_image1.jpg")

        # Prepare form data for the POST request
        form_data = {
            "media_files": [test_file1, test_file2],
        }

        response = self.client.post(
            self.media_url,
            data=form_data,
            format="multipart",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify new media was added
        assert self.product.media.count() == 4  # 2 original + 2 new  # noqa: PLR2004

        # Check response contains all media files
        data = response.json()
        assert len(data) == 4  # noqa: PLR2004

        # Verify file types in the database
        file_types = set()
        for media in self.product.media.all():
            if media.media_file.name.endswith(".pdf"):
                file_types.add("pdf")
            elif media.media_file.name.endswith((".jpg", ".jpeg", ".png")):
                file_types.add("image")

        assert "pdf" in file_types
        assert "image" in file_types

    def test_delete_media_success(self):
        """Test successful deletion of media files by product owner"""
        # Login as the product owner
        self.client.login(
            username="mediacoach",
            password="StrongPassword123",  # noqa: S106
        )

        # Get the initial media file paths to check later if files are deleted
        media1_path = self.media1.media_file.path

        # Store initial media IDs
        initial_media_ids = list(self.product.media.values_list("id", flat=True))

        # Prepare data for deleting one media file
        delete_data = {
            "delete_ids": [self.media1.id],
        }

        response = self.client.post(
            self.media_url,
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify one media was deleted
        assert self.product.media.count() == 1

        # Check the file was physically deleted
        assert not Path(media1_path).exists()

        # Verify the remaining media is the one we didn't delete
        remaining_id = self.product.media.first().id
        assert remaining_id == self.media2.id
        assert remaining_id in initial_media_ids
        assert self.media1.id not in self.product.media.values_list("id", flat=True)

    def test_add_and_delete_media_simultaneously(self):
        """Test simultaneously adding and deleting media files"""
        # Login as the product owner
        self.client.login(
            username="mediacoach",
            password="StrongPassword123",  # noqa: S106
        )

        new_file = self._create_test_file("another_file.pdf")

        # Prepare form data for adding one file and deleting one file

        response = self.client.post(
            self.media_url,
            data={"media_files": [new_file], "delete_ids": [self.media1.id]},
            format="multipart",
        )

        assert response.status_code == status.HTTP_200_OK

        # Should still have 2 files (deleted 1, added 1)
        assert self.product.media.count() == 2  # noqa: PLR2004

        # Verify the media1 was deleted and new file was added
        current_ids = list(self.product.media.values_list("id", flat=True))
        assert self.media1.id not in current_ids
        assert self.media2.id in current_ids

    def test_delete_nonexistent_media(self):
        """Test deleting non-existent media IDs"""
        # Login as the product owner
        self.client.login(
            username="mediacoach",
            password="StrongPassword123",  # noqa: S106
        )

        # Use a non-existent ID
        non_existent_id = 9999

        # Prepare data for deleting one non-existent media file
        delete_data = {
            "delete_ids": [non_existent_id],
        }

        response = self.client.post(
            self.media_url,
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        # This should still return 200 OK, as Django's delete() with non-existent IDs is a no-op  # noqa: E501
        assert response.status_code == status.HTTP_200_OK

        # No media should be deleted
        assert self.product.media.count() == 2  # noqa: PLR2004
