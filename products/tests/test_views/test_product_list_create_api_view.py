import json

import pytest
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from coach.models import Coach
from coach.models import CoachReview
from coach.tests.factories import CoachFactory
from coach.tests.factories import CoachReviewFactory
from core.users.models import User
from products.models import Product
from products.tests.factories import ProductCategoryFactory
from products.tests.factories import ProductFactory
from products.tests.factories import ProductTypeFactory
from products.tests.factories import create_test_image


@pytest.mark.django_db
class ProductListCreateAPIViewTestCase(TestCase):
    # Test constants
    EXPECTED_TOTAL_PRODUCTS = 3
    EXPECTED_CATEGORY1_PRODUCTS = 2
    EXPECTED_CATEGORY2_PRODUCTS = 1
    EXPECTED_COACH1_PRODUCTS = 2
    EXPECTED_COACH2_PRODUCTS = 1
    EXPECTED_TYPE1_PRODUCTS = 2
    EXPECTED_TYPE2_PRODUCTS = 1
    EXPECTED_EN_PRODUCTS = 1
    EXPECTED_ES_PRODUCTS = 1
    EXPECTED_FR_PRODUCTS = 1
    EXPECTED_FEATURED_PRODUCTS = 1
    EXPECTED_NON_FEATURED_PRODUCTS = 3
    EXTRA_PRODUCTS_COUNT = 8
    TOTAL_PRODUCTS_WITH_EXTRA = 11
    DEFAULT_PAGE_SIZE = 10
    SECOND_PAGE_SIZE = 1

    # Price constants
    PRODUCT1_PRICE = 99.99
    PRODUCT2_PRICE = 149.99
    PRODUCT3_PRICE = 199.99
    PRICE_FILTER_MIN = 100
    PRICE_FILTER_MID = 150
    PRICE_FILTER_MAX = 180
    PRICE_FILTER_HIGH = 200

    # Coach rating constants
    COACH1_EXPECTED_AVG_RATING = 4.5
    COACH1_EXPECTED_REVIEW_COUNT = 2
    COACH2_EXPECTED_AVG_RATING = 3.0
    COACH2_EXPECTED_REVIEW_COUNT = 1

    def setUp(self):
        self.client = Client()
        self.list_url = reverse("products:list-create")

        # Use coach type constant instead of CoachType model
        self.coach_type = Coach.TYPE_ONLINE

        # Create coaches
        self.coach1 = CoachFactory(
            first_name="Coach",
            last_name="Alpha",
            type=self.coach_type,
            website="https://coachalpha.com",
            email="alpha@example.com",
        )

        self.coach2 = CoachFactory(
            first_name="Coach",
            last_name="Beta",
            type=self.coach_type,
            website="https://coachbeta.com",
            email="beta@example.com",
        )

        # Create product categories
        self.category1 = ProductCategoryFactory(
            name="Category One",
            description="First category for testing",
        )

        self.category2 = ProductCategoryFactory(
            name="Category Two",
            description="Second category for testing",
        )

        # Create product types
        self.product_type1 = ProductTypeFactory(
            name="Course",
            description="Educational course content",
        )

        self.product_type2 = ProductTypeFactory(
            name="Workshop",
            description="Interactive workshop content",
        )

        # Create products
        self.product1 = ProductFactory(
            name="Product One",
            description="This is product one",
            price="99.99",
            language="en",
            coach=self.coach1,
            category=self.category1,
            product_type=self.product_type1,
        )

        self.product2 = ProductFactory(
            name="Product Two",
            description="This is product two",
            price="149.99",
            language="es",
            coach=self.coach1,
            category=self.category2,
            product_type=self.product_type2,
        )

        self.product3 = ProductFactory(
            name="Different Product",
            description="Premium coaching content",
            price="199.99",
            language="fr",
            coach=self.coach2,
            category=self.category1,
            product_type=self.product_type1,
        )

        # Create coach reviews to test avg_rating and review_count
        self.approved_review1 = CoachReviewFactory(
            coach=self.coach1,
            rating=5,
            status=CoachReview.STATUS_APPROVED,
        )
        self.approved_review2 = CoachReviewFactory(
            coach=self.coach1,
            rating=4,
            status=CoachReview.STATUS_APPROVED,
        )
        # Pending review should not affect avg_rating/review_count
        self.pending_review = CoachReviewFactory(
            coach=self.coach1,
            rating=1,
            status=CoachReview.STATUS_PENDING,
        )
        self.approved_review3 = CoachReviewFactory(
            coach=self.coach2,
            rating=3,
            status=CoachReview.STATUS_APPROVED,
        )

    def test_list_products_success(self):
        """Test successful retrieval of products list"""
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "count" in data
        assert "results" in data
        assert data["count"] == self.EXPECTED_TOTAL_PRODUCTS

        # Check first result has expected fields
        first_product = data["results"][0]
        assert "id" in first_product
        assert "name" in first_product
        assert "description" in first_product
        assert "price" in first_product
        assert "language" in first_product
        assert "product_type" in first_product
        assert "image" in first_product
        assert "category" in first_product
        assert "coach" in first_product
        assert "created_at" in first_product

        # Check coach fields include avg_rating and review_count
        coach_data = first_product["coach"]
        assert "avg_rating" in coach_data
        assert "review_count" in coach_data

    def test_coach_avg_rating_and_review_count_in_product_list(self):
        """Test coach avg_rating and review_count in product list"""
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        products = data["results"]

        # Find products by coach to test rating calculations
        coach1_products = [p for p in products if p["coach"]["id"] == self.coach1.id]
        coach2_products = [p for p in products if p["coach"]["id"] == self.coach2.id]

        # Coach1 has 2 approved reviews (ratings: 5, 4) -> avg: 4.5, count: 2
        for product in coach1_products:
            coach_data = product["coach"]
            assert coach_data["avg_rating"] == self.COACH1_EXPECTED_AVG_RATING
            assert coach_data["review_count"] == self.COACH1_EXPECTED_REVIEW_COUNT

        # Coach2 has 1 approved review (rating: 3) -> avg: 3.0, count: 1
        for product in coach2_products:
            coach_data = product["coach"]
            assert coach_data["avg_rating"] == self.COACH2_EXPECTED_AVG_RATING
            assert coach_data["review_count"] == self.COACH2_EXPECTED_REVIEW_COUNT

    def test_pagination(self):
        """Test pagination functionality"""
        # Create 8 more products to have a total of 11 (exceeding default page size of 10)  # noqa: E501
        for i in range(self.EXTRA_PRODUCTS_COUNT):
            ProductFactory(
                name=f"Extra Product {i}",
                coach=self.coach1,
                category=self.category1,
            )

        response = self.client.get(self.list_url)
        data = response.json()

        assert data["count"] == self.TOTAL_PRODUCTS_WITH_EXTRA
        assert len(data["results"]) == self.DEFAULT_PAGE_SIZE
        assert data["next"] is not None  # Should have next page

        # Get second page
        response = self.client.get(data["next"])
        data = response.json()

        assert len(data["results"]) == self.SECOND_PAGE_SIZE

    def test_filtering_by_category(self):
        """Test filtering products by category"""
        response = self.client.get(f"{self.list_url}?category__id={self.category1.id}")
        data = response.json()

        assert data["count"] == self.EXPECTED_CATEGORY1_PRODUCTS
        assert all(
            product["category"]["id"] == self.category1.id
            for product in data["results"]
        )

        # Test filtering by category slug
        response = self.client.get(
            f"{self.list_url}?category__slug={self.category2.slug}",
        )
        data = response.json()

        assert data["count"] == self.EXPECTED_CATEGORY2_PRODUCTS
        assert data["results"][0]["category"]["slug"] == self.category2.slug

    def test_filtering_by_coach(self):
        """Test filtering products by coach"""
        response = self.client.get(f"{self.list_url}?coach__id={self.coach1.id}")
        data = response.json()

        assert data["count"] == self.EXPECTED_COACH1_PRODUCTS
        assert all(
            product["coach"]["id"] == self.coach1.id for product in data["results"]
        )

        # Test filtering by coach name (now split into first_name and last_name)
        full_name = f"{self.coach2.first_name} {self.coach2.last_name}"
        response = self.client.get(f"{self.list_url}?search={full_name}")
        data = response.json()

        assert data["count"] == self.EXPECTED_COACH2_PRODUCTS
        assert data["results"][0]["coach"]["first_name"] == self.coach2.first_name
        assert data["results"][0]["coach"]["last_name"] == self.coach2.last_name

    def test_search_functionality(self):
        """Test search functionality"""
        # Search by product name
        response = self.client.get(f"{self.list_url}?search=Different")
        data = response.json()

        assert data["count"] == 1
        assert "Different" in data["results"][0]["name"]

        # Search by description
        response = self.client.get(f"{self.list_url}?search=Premium")
        data = response.json()

        assert data["count"] == 1
        assert "Premium" in data["results"][0]["description"]

    def test_ordering_functionality(self):
        """Test ordering functionality"""
        # Order by name ascending
        response = self.client.get(f"{self.list_url}?ordering=name")
        data = response.json()

        names = [product["name"] for product in data["results"]]
        assert names == sorted(names)

        # Order by price descending
        response = self.client.get(f"{self.list_url}?ordering=-price")
        data = response.json()

        prices = [float(product["price"]) for product in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_custom_page_size(self):
        """Test custom page size parameter"""
        response = self.client.get(f"{self.list_url}?page_size=2")
        data = response.json()

        assert len(data["results"]) == 2  # noqa: PLR2004
        assert data["next"] is not None

    def test_create_product_unauthenticated(self):
        """Test creating product without authentication fails"""
        payload = {
            "name": "New Product",
            "description": "A new product description",
            "price": "129.99",
            "category_id": self.category1.id,
        }

        response = self.client.post(
            self.list_url,
            json.dumps(payload),
            content_type="application/json",
        )

        # Should fail because auth is required
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_product_success(self):
        """Test successful creation of a product by an authenticated coach"""
        # Create a user for authentication
        user = User.objects.create_user(
            username="testcoach",
            email="testcoach@example.com",
            password="StrongPassword123",  # noqa: S106
            is_active=True,
        )

        # Link the user to coach1
        self.coach1.user = user
        self.coach1.save()

        # Login
        self.client.login(
            username="testcoach",
            password="StrongPassword123",  # noqa: S106
        )

        # Create test image
        test_image = create_test_image("new_product.jpg")

        # Prepare form data for the POST request
        form_data = {
            "name": "New Created Product",
            "description": "This is a newly created product",
            "price": "129.99",
            "category_id": str(self.category1.id),
            "image": test_image,
        }

        # Use POST request with multipart form data
        response = self.client.post(
            self.list_url,
            data=form_data,
            format="multipart",
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Get the created product from response
        data = response.json()
        assert data["name"] == form_data["name"]
        assert data["description"] == form_data["description"]
        assert float(data["price"]) == float(form_data["price"])
        assert data["category"]["id"] == int(form_data["category_id"])
        assert data["coach"]["id"] == self.coach1.id

        # Verify product was actually created in database
        product_exists = Product.objects.filter(name=form_data["name"]).exists()
        assert product_exists

    def test_create_product_invalid_data(self):
        """Test creating product with invalid data fails"""
        # Create and login user
        user = User.objects.create_user(
            username="testcoach2",
            email="testcoach2@example.com",
            password="StrongPassword123",  # noqa: S106
            is_active=True,
        )

        self.coach1.user = user
        self.coach1.save()

        self.client.login(
            username="testcoach2",
            password="StrongPassword123",  # noqa: S106
        )

        # Invalid payload (missing required fields)
        invalid_payload = {
            "name": "",  # Empty name should be invalid
            "price": "invalid-price",  # Invalid price format
        }

        response = self.client.post(
            self.list_url,
            json.dumps(invalid_payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.json()  # Should contain validation error for name

    def test_create_product_user_without_coach(self):
        """Test creating product by user without coach fails"""
        # Create a regular user without a coach association
        User.objects.create_user(
            username="regularuser",
            email="regularuser@example.com",
            password="StrongPassword123",  # noqa: S106
            is_active=True,
        )

        # Login as the regular user
        self.client.login(
            username="regularuser",
            password="StrongPassword123",  # noqa: S106
        )

        # Create test image
        test_image = create_test_image("regular_user_product.jpg")

        # Prepare form data for the POST request
        form_data = {
            "name": "Product by Regular User",
            "description": "This product should not be created",
            "price": "99.99",
            "category_id": str(self.category1.id),
            "image": test_image,
        }

        # Attempt to create product
        response = self.client.post(
            self.list_url,
            data=form_data,
            format="multipart",
        )

        # Should fail because user is not a coach
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Verify no product was created
        product_exists = Product.objects.filter(name=form_data["name"]).exists()
        assert not product_exists

    def test_filtering_by_is_featured(self):
        """Test filtering products by is_featured field"""
        # Create a featured product
        ProductFactory(
            name="Featured Product",
            description="This is a featured product",
            coach=self.coach1,
            category=self.category1,
            is_featured=True,
        )

        # Set existing products as not featured (they default to False from factory)
        self.product1.is_featured = False
        self.product1.save()
        self.product2.is_featured = False
        self.product2.save()
        self.product3.is_featured = False
        self.product3.save()

        # Test filtering for featured products
        response = self.client.get(f"{self.list_url}?is_featured=true")
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["is_featured"] is True
        assert data["results"][0]["name"] == "Featured Product"

        # Test filtering for non-featured products
        response = self.client.get(f"{self.list_url}?is_featured=false")
        data = response.json()

        assert data["count"] == self.EXPECTED_NON_FEATURED_PRODUCTS
        assert all(product["is_featured"] is False for product in data["results"])

        # Test that is_featured field is included in response
        response = self.client.get(self.list_url)
        data = response.json()
        for product in data["results"]:
            assert "is_featured" in product

    def test_product_factory_is_featured_field(self):
        """Test that ProductFactory creates products with is_featured field"""
        # Test default value
        default_product = ProductFactory(coach=self.coach1, category=self.category1)
        assert default_product.is_featured is False

        # Test setting is_featured=True
        featured_product = ProductFactory(
            coach=self.coach1,
            category=self.category1,
            is_featured=True,
        )
        assert featured_product.is_featured is True

    def test_create_product_with_is_featured(self):
        """Test creating a product with is_featured field"""
        # Create a user for authentication
        user = User.objects.create_user(
            username="featuredcoach",
            email="featuredcoach@example.com",
            password="StrongPassword123",  # noqa: S106
            is_active=True,
        )

        # Link the user to coach1
        self.coach1.user = user
        self.coach1.save()

        # Login
        self.client.login(
            username="featuredcoach",
            password="StrongPassword123",  # noqa: S106
        )

        # Create test image
        test_image = create_test_image("featured_product.jpg")

        # Prepare form data for the POST request with is_featured=True
        form_data = {
            "name": "Featured Product",
            "description": "This is a featured product",
            "price": "199.99",
            "category_id": str(self.category1.id),
            "is_featured": "true",
            "image": test_image,
        }

        # Use POST request with multipart form data
        response = self.client.post(
            self.list_url,
            data=form_data,
            format="multipart",
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Get the created product from response
        data = response.json()
        assert data["name"] == form_data["name"]
        assert data["is_featured"] is True

        # Verify product was actually created in database with correct is_featured value
        created_product = Product.objects.get(name=form_data["name"])
        assert created_product.is_featured is True

        # Test creating product with is_featured=False
        form_data_not_featured = {
            "name": "Not Featured Product",
            "description": "This is not a featured product",
            "price": "99.99",
            "category_id": str(self.category2.id),
            "is_featured": "false",
            "image": create_test_image("not_featured_product.jpg"),
        }

        response = self.client.post(
            self.list_url,
            data=form_data_not_featured,
            format="multipart",
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["is_featured"] is False

        # Verify in database
        created_product = Product.objects.get(name=form_data_not_featured["name"])
        assert created_product.is_featured is False

    def test_filtering_by_product_type(self):
        """Test filtering products by product type"""
        # Filter by product type ID
        response = self.client.get(
            f"{self.list_url}?product_type__id={self.product_type1.id}",
        )
        data = response.json()

        assert data["count"] == self.EXPECTED_TYPE1_PRODUCTS
        assert all(
            product["product_type"]["id"] == self.product_type1.id
            for product in data["results"]
        )

        # Filter by product type name
        response = self.client.get(
            f"{self.list_url}?product_type__name={self.product_type2.name}",
        )
        data = response.json()

        assert data["count"] == self.EXPECTED_TYPE2_PRODUCTS
        assert data["results"][0]["product_type"]["name"] == self.product_type2.name

    def test_filtering_by_language(self):
        """Test filtering products by language"""
        # Filter by English language
        response = self.client.get(f"{self.list_url}?language=en")
        data = response.json()

        assert data["count"] == self.EXPECTED_EN_PRODUCTS
        assert data["results"][0]["language"] == "en"

        # Filter by Spanish language
        response = self.client.get(f"{self.list_url}?language=es")
        data = response.json()

        assert data["count"] == self.EXPECTED_ES_PRODUCTS
        assert data["results"][0]["language"] == "es"

        # Filter by French language
        response = self.client.get(f"{self.list_url}?language=fr")
        data = response.json()

        assert data["count"] == self.EXPECTED_FR_PRODUCTS
        assert data["results"][0]["language"] == "fr"

    def test_filtering_by_price(self):
        """Test filtering products by price (exact, gte, lte)"""
        # Test exact price filtering
        response = self.client.get(f"{self.list_url}?price={self.PRODUCT1_PRICE}")
        data = response.json()

        assert data["count"] == self.EXPECTED_EN_PRODUCTS
        assert float(data["results"][0]["price"]) == self.PRODUCT1_PRICE

        # Test price greater than or equal (gte)
        response = self.client.get(
            f"{self.list_url}?price__gte={self.PRICE_FILTER_MID}",
        )
        data = response.json()

        assert data["count"] == self.EXPECTED_FR_PRODUCTS  # Only product3 >= 150
        assert all(
            float(product["price"]) >= self.PRICE_FILTER_MID
            for product in data["results"]
        )

        # Test price less than or equal (lte)
        response = self.client.get(
            f"{self.list_url}?price__lte={self.PRICE_FILTER_MID}",
        )
        data = response.json()

        assert data["count"] == self.EXPECTED_CATEGORY1_PRODUCTS  # product1+2 <= 150
        assert all(
            float(product["price"]) <= self.PRICE_FILTER_MID
            for product in data["results"]
        )

        # Test price range using both gte and lte
        response = self.client.get(
            f"{self.list_url}?price__gte={self.PRICE_FILTER_MIN}&price__lte={self.PRICE_FILTER_MAX}",
        )
        data = response.json()

        assert data["count"] == self.EXPECTED_ES_PRODUCTS
        price = float(data["results"][0]["price"])
        assert self.PRICE_FILTER_MIN <= price <= self.PRICE_FILTER_MAX

    def test_combined_filtering(self):
        """Test combining multiple filters"""
        # Filter by category and language
        response = self.client.get(
            f"{self.list_url}?category__id={self.category1.id}&language=en",
        )
        data = response.json()

        assert data["count"] == self.EXPECTED_EN_PRODUCTS
        assert data["results"][0]["category"]["id"] == self.category1.id
        assert data["results"][0]["language"] == "en"

        # Filter by product type and price range
        response = self.client.get(
            f"{self.list_url}?product_type__id={self.product_type1.id}&price__gte={self.PRICE_FILTER_MAX}",
        )
        data = response.json()

        assert data["count"] == self.EXPECTED_FR_PRODUCTS
        assert data["results"][0]["product_type"]["id"] == self.product_type1.id
        assert float(data["results"][0]["price"]) >= self.PRICE_FILTER_MAX

        # Filter by coach, language, and price
        response = self.client.get(
            f"{self.list_url}?coach__id={self.coach1.id}&language=es&price__lte={self.PRICE_FILTER_HIGH}",
        )
        data = response.json()

        assert data["count"] == self.EXPECTED_ES_PRODUCTS
        result = data["results"][0]
        assert result["coach"]["id"] == self.coach1.id
        assert result["language"] == "es"
        assert float(result["price"]) <= self.PRICE_FILTER_HIGH

    def test_is_saved_and_is_saved_uuid_fields_for_unauthenticated_user(self):
        """Test that is_saved and is_saved_uuid fields work for unauthenticated users"""
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Check that all products have is_saved=False and is_saved_uuid=None for
        # unauthenticated users
        for product in data["results"]:
            assert "is_saved" in product
            assert "is_saved_uuid" in product
            assert product["is_saved"] is False
            assert product["is_saved_uuid"] is None

    def test_is_saved_and_is_saved_uuid_fields_for_authenticated_user(self):
        """Test that is_saved and is_saved_uuid fields work correctly for
        authenticated users"""
        from core.users.tests.factories import UserFactory
        from products.tests.factories import SavedProductFactory

        # Create a user and authenticate
        user = UserFactory()
        self.client.force_login(user)

        # Save one of the products for this user
        saved_product = SavedProductFactory(user=user, product=self.product1)

        # Make request to list API
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        products_data = {product["id"]: product for product in data["results"]}

        # Check that saved product has is_saved=True and correct is_saved_uuid
        assert "is_saved" in products_data[self.product1.id]
        assert "is_saved_uuid" in products_data[self.product1.id]
        assert products_data[self.product1.id]["is_saved"] is True
        assert products_data[self.product1.id]["is_saved_uuid"] == str(
            saved_product.uuid,
        )

        # Check that non-saved products have is_saved=False and is_saved_uuid=None
        assert products_data[self.product2.id]["is_saved"] is False
        assert products_data[self.product2.id]["is_saved_uuid"] is None
        assert products_data[self.product3.id]["is_saved"] is False
        assert products_data[self.product3.id]["is_saved_uuid"] is None

    def test_is_saved_uuid_field_functionality_multiple_users(self):
        """Test is_saved_uuid field functionality with multiple users."""
        from core.users.tests.factories import UserFactory
        from products.tests.factories import SavedProductFactory

        # Create two different users
        user1 = UserFactory()
        user2 = UserFactory()

        # Create saved product records for different users
        saved_product1 = SavedProductFactory(user=user1, product=self.product1)
        saved_product2 = SavedProductFactory(user=user2, product=self.product2)

        # Test with user1 authentication
        self.client.force_login(user1)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        products_data = {product["id"]: product for product in data["results"]}

        # User1 should see their saved product with correct UUID
        assert products_data[self.product1.id]["is_saved"] is True
        assert products_data[self.product1.id]["is_saved_uuid"] == str(
            saved_product1.uuid,
        )

        # User1 should not see product2 as saved (different user)
        assert products_data[self.product2.id]["is_saved"] is False
        assert products_data[self.product2.id]["is_saved_uuid"] is None

        # Product3 is not saved by anyone
        assert products_data[self.product3.id]["is_saved"] is False
        assert products_data[self.product3.id]["is_saved_uuid"] is None

        # Test with user2 authentication
        self.client.force_login(user2)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        products_data = {product["id"]: product for product in data["results"]}

        # User2 should not see product1 as saved (different user)
        assert products_data[self.product1.id]["is_saved"] is False
        assert products_data[self.product1.id]["is_saved_uuid"] is None

        # User2 should see their saved product with correct UUID
        assert products_data[self.product2.id]["is_saved"] is True
        assert products_data[self.product2.id]["is_saved_uuid"] == str(
            saved_product2.uuid,
        )

        # Product3 is still not saved by anyone
        assert products_data[self.product3.id]["is_saved"] is False
        assert products_data[self.product3.id]["is_saved_uuid"] is None

        # Test after logout (unauthenticated)
        self.client.logout()
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # All products should show as not saved for unauthenticated users
        for product in data["results"]:
            assert product["is_saved"] is False
            assert product["is_saved_uuid"] is None
