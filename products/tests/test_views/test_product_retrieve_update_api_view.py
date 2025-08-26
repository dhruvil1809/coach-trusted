import json
from decimal import Decimal
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from coach.models import Coach
from coach.models import CoachReview
from coach.tests.factories import CoachFactory
from coach.tests.factories import CoachReviewFactory
from core.users.models import User
from products.tests.factories import ProductCategoryFactory
from products.tests.factories import ProductFactory
from products.tests.factories import create_test_image


@pytest.mark.django_db
class ProductRetrieveUpdateAPIViewTestCase(TestCase):
    # Test constants for coach ratings
    EXPECTED_AVG_RATING = 4.0
    EXPECTED_REVIEW_COUNT = 2

    # Rating breakdown test constants
    EXPECTED_5_STAR_COUNT = 2
    EXPECTED_4_STAR_COUNT = 1
    EXPECTED_3_STAR_COUNT = 1
    EXPECTED_2_STAR_COUNT = 1
    EXPECTED_1_STAR_COUNT = 0
    EXPECTED_TOTAL_REVIEWS = 5

    def setUp(self):
        self.client = APIClient()  # Using APIClient instead of Django's Client

        self.coach_type = Coach.TYPE_ONLINE

        # Create users
        self.user1 = User.objects.create_user(
            username="coachuser",
            email="coach@example.com",
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
            first_name="Test",
            last_name="Coach",
            type=self.coach_type,
            website="https://testcoach.com",
            email="testcoach@example.com",
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
            name="Test Category",
            description="Category for testing",
        )

        # Create a product
        self.product = ProductFactory(
            name="Test Product",
            description="This is a test product",
            price=Decimal("99.99"),
            coach=self.coach1,
            category=self.category,
            image=create_test_image("product.jpg"),
        )

        # URL for product detail
        self.detail_url = reverse(
            "products:retrieve-update",
            kwargs={"slug": self.product.slug},
        )

        # Create coach reviews to test avg_rating and review_count
        self.approved_review1 = CoachReviewFactory(
            coach=self.coach1,
            rating=5,
            status=CoachReview.STATUS_APPROVED,
        )
        self.approved_review2 = CoachReviewFactory(
            coach=self.coach1,
            rating=3,
            status=CoachReview.STATUS_APPROVED,
        )
        # Pending review should not affect avg_rating/review_count
        self.pending_review = CoachReviewFactory(
            coach=self.coach1,
            rating=1,
            status=CoachReview.STATUS_PENDING,
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

    def test_retrieve_product_success(self):
        """Test successful retrieval of a product (no authentication required)"""
        response = self.client.get(self.detail_url)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["name"] == self.product.name
        assert data["description"] == self.product.description
        assert Decimal(data["price"]) == self.product.price
        assert data["category"]["id"] == self.category.id
        assert data["coach"]["id"] == self.coach1.id

        # Check coach fields include avg_rating and review_count
        coach_data = data["coach"]
        assert "avg_rating" in coach_data
        assert "review_count" in coach_data
        assert coach_data["avg_rating"] == self.EXPECTED_AVG_RATING
        assert coach_data["review_count"] == self.EXPECTED_REVIEW_COUNT

    def test_coach_avg_rating_and_review_count_in_product_detail(self):
        """Test coach avg_rating and review_count are correctly calculated"""
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        coach_data = data["coach"]

        # Coach1 has 2 approved reviews (ratings: 5, 3) -> avg: 4.0, count: 2
        # Pending review (rating: 1) should not be included
        assert coach_data["avg_rating"] == self.EXPECTED_AVG_RATING
        assert coach_data["review_count"] == self.EXPECTED_REVIEW_COUNT

        # Verify the coach ID matches
        assert coach_data["id"] == self.coach1.id

    def test_coach_with_no_approved_reviews(self):
        """Test coach with no approved reviews has avg_rating 0.0 and review_count 0"""
        # Create a product with coach2 who has no reviews
        product_no_reviews = ProductFactory(
            name="Product No Reviews",
            description="Product with coach having no reviews",
            price=Decimal("50.00"),
            coach=self.coach2,
            category=self.category,
        )

        detail_url_no_reviews = reverse(
            "products:retrieve-update",
            kwargs={"slug": product_no_reviews.slug},
        )

        response = self.client.get(detail_url_no_reviews)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        coach_data = data["coach"]

        # Coach2 has no approved reviews -> avg_rating: 0.0, review_count: 0
        assert coach_data["avg_rating"] == 0.0
        assert coach_data["review_count"] == 0
        assert coach_data["id"] == self.coach2.id

    def test_coach_rating_breakdown_in_product_detail(self):
        """Test that coach rating_breakdown is correctly populated in product detail"""
        # Create additional reviews to test different rating breakdowns
        CoachReviewFactory(
            coach=self.coach1,
            rating=5,
            status=CoachReview.STATUS_APPROVED,
        )
        CoachReviewFactory(
            coach=self.coach1,
            rating=4,
            status=CoachReview.STATUS_APPROVED,
        )
        CoachReviewFactory(
            coach=self.coach1,
            rating=2,
            status=CoachReview.STATUS_APPROVED,
        )
        # Create a pending review that shouldn't be counted
        CoachReviewFactory(
            coach=self.coach1,
            rating=1,
            status=CoachReview.STATUS_PENDING,
        )

        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        coach_data = data["coach"]

        # Check that rating_breakdown exists
        assert "rating_breakdown" in coach_data
        rating_breakdown = coach_data["rating_breakdown"]

        # Verify the rating breakdown structure
        assert "5_star" in rating_breakdown
        assert "4_star" in rating_breakdown
        assert "3_star" in rating_breakdown
        assert "2_star" in rating_breakdown
        assert "1_star" in rating_breakdown

        # Verify the counts (only approved reviews should be counted)
        # Initial setup: 2 reviews (5-star, 3-star)
        # Additional: 1 five-star, 1 four-star, 1 two-star
        # Total: 2 five-star, 1 four-star, 1 three-star, 1 two-star, 0 one-star
        assert rating_breakdown["5_star"] == self.EXPECTED_5_STAR_COUNT
        assert rating_breakdown["4_star"] == self.EXPECTED_4_STAR_COUNT
        assert rating_breakdown["3_star"] == self.EXPECTED_3_STAR_COUNT
        assert rating_breakdown["2_star"] == self.EXPECTED_2_STAR_COUNT
        assert rating_breakdown["1_star"] == self.EXPECTED_1_STAR_COUNT

        # Verify total count matches review_count
        total_breakdown = sum(rating_breakdown.values())
        assert coach_data["review_count"] == total_breakdown
        assert coach_data["review_count"] == self.EXPECTED_TOTAL_REVIEWS

    def test_update_product_success(self):
        """Test successful update of a product by the owner"""
        # Login as the coach's user
        self.client.login(
            username="coachuser",
            password="StrongPassword123",  # noqa: S106
        )

        # Store the original image path
        original_image_path = self.product.image.path

        # Create a new test image for the update
        test_image = self._create_test_image("updated_product.jpg", (200, 200), "red")

        # Prepare multipart form data for the PUT request
        form_data = {
            "name": "Updated Product Name",
            "description": "Updated product description",
            "price": "149.99",
            "category_id": str(self.category.id),
            "image": test_image,
        }

        # Use PUT request with multipart form data, explicitly setting format
        response = self.client.put(
            self.detail_url,
            data=form_data,
            format="multipart",  # Explicitly set format to multipart
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify product was updated
        self.product.refresh_from_db()
        assert self.product.name == form_data["name"]
        assert self.product.description == form_data["description"]
        assert self.product.price == Decimal(form_data["price"])
        assert self.product.category.id == int(form_data["category_id"])

        # Verify the image was updated
        assert self.product.image is not None
        assert self.product.image.path != original_image_path

    def test_update_product_unauthenticated(self):
        """Test updating product without authentication fails"""
        response = self.client.put(
            self.detail_url,
            json.dumps(
                {
                    "name": "Updated Product Name",
                    "description": "Updated product description",
                    "price": "149.99",
                    "category_id": self.category.id,
                },
            ),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_product_wrong_user(self):
        """Test updating product by a different coach fails"""
        # Login as a different user (not the product owner's coach)
        self.client.login(
            username="otheruser",
            password="StrongPassword123",  # noqa: S106
        )

        response = self.client.put(
            self.detail_url,
            json.dumps(
                {
                    "name": "Updated Product Name",
                    "description": "Updated product description",
                    "price": "149.99",
                    "category_id": self.category.id,
                },
            ),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_product_invalid_data(self):
        """Test updating product with invalid data fails"""
        # Login as the coach's user
        self.client.login(
            username="coachuser",
            password="StrongPassword123",  # noqa: S106
        )

        invalid_payload = {
            "name": "",  # Empty name should be invalid
            "price": "invalid-price",  # Invalid price format
        }

        response = self.client.put(
            self.detail_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Ensure the product data was not changed
        self.product.refresh_from_db()
        assert self.product.name != invalid_payload["name"]

    def test_partial_update_product(self):
        """Test partial update (PATCH) of a product"""
        # Login as the coach's user
        self.client.login(
            username="coachuser",
            password="StrongPassword123",  # noqa: S106
        )

        # Update only the name
        partial_update = {"name": "Partially Updated Name"}

        response = self.client.patch(
            self.detail_url,
            json.dumps(partial_update),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify only name was updated while other fields remain unchanged
        self.product.refresh_from_db()
        assert self.product.name == partial_update["name"]
        assert self.product.description == "This is a test product"  # Original value
        assert self.product.price == Decimal("99.99")  # Original value

    def test_retrieve_nonexistent_product(self):
        """Test 404 response when trying to retrieve a non-existent product"""
        non_existent_url = reverse(
            "products:retrieve-update",
            kwargs={"slug": "non-existent-slug"},
        )
        response = self.client.get(non_existent_url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_product_is_featured_field(self):
        """Test updating the is_featured field of a product"""
        # Login as the coach's user
        self.client.login(
            username="coachuser",
            password="StrongPassword123",  # noqa: S106
        )

        # Verify initial state
        assert self.product.is_featured is False

        # Update product to be featured
        form_data = {
            "name": self.product.name,
            "description": self.product.description,
            "price": str(self.product.price),
            "category_id": str(self.product.category.id),
            "product_type_id": (
                str(self.product.product_type.id) if self.product.product_type else ""
            ),
            "language": self.product.language,
            "is_featured": "true",
        }

        response = self.client.put(
            self.detail_url,
            data=form_data,
            format="multipart",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify product was updated
        self.product.refresh_from_db()
        assert self.product.is_featured is True

        # Verify response contains is_featured field
        data = response.json()
        assert data["is_featured"] is True

        # Update product to not be featured
        form_data["is_featured"] = "false"

        response = self.client.put(
            self.detail_url,
            data=form_data,
            format="multipart",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify product was updated
        self.product.refresh_from_db()
        assert self.product.is_featured is False

        # Verify response contains is_featured field
        data = response.json()
        assert data["is_featured"] is False

    def test_is_saved_and_is_saved_uuid_fields_for_unauthenticated_user(self):
        """Test that is_saved and is_saved_uuid fields work for unauthenticated users"""
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "is_saved" in data
        assert "is_saved_uuid" in data
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None

    def test_is_saved_and_is_saved_uuid_fields_for_authenticated_user(self):
        """Test that is_saved and is_saved_uuid fields work correctly for
        authenticated users"""
        from core.users.tests.factories import UserFactory
        from products.tests.factories import SavedProductFactory

        # Create a user different from the product's coach
        user = UserFactory()

        # Test without saving the product first
        self.client.force_login(user)
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "is_saved" in data
        assert "is_saved_uuid" in data
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None

        # Now save the product for this user
        saved_product = SavedProductFactory(user=user, product=self.product)

        # Make request again
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "is_saved" in data
        assert "is_saved_uuid" in data
        assert data["is_saved"] is True
        assert data["is_saved_uuid"] == str(saved_product.uuid)

    def test_is_saved_uuid_field_functionality_detail_view(self):
        """Test comprehensive functionality of is_saved_uuid field in detail view"""
        from core.users.tests.factories import UserFactory
        from products.tests.factories import SavedProductFactory

        # Create two different users
        user1 = UserFactory()
        user2 = UserFactory()

        # Test with user1 - product not saved
        self.client.force_login(user1)
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None

        # Save the product for user1
        saved_product = SavedProductFactory(user=user1, product=self.product)

        # Test again - should now show as saved with UUID
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_saved"] is True
        assert data["is_saved_uuid"] == str(saved_product.uuid)

        # Test with user2 - should not see product as saved (different user)
        self.client.force_login(user2)
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None

        # Save the product for user2 as well
        saved_product2 = SavedProductFactory(user=user2, product=self.product)

        # Test again - user2 should see their own saved UUID
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_saved"] is True
        assert data["is_saved_uuid"] == str(saved_product2.uuid)
        # Should be different from user1's UUID
        assert data["is_saved_uuid"] != str(saved_product.uuid)

        # Test unauthenticated access
        self.client.logout()
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_saved"] is False
        assert data["is_saved_uuid"] is None
