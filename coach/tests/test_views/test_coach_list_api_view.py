import pytest
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from coach.models import Coach
from coach.models import CoachReview
from coach.tests.factories import CoachFactory
from coach.tests.factories import CoachReviewFactory


@pytest.mark.django_db
class CoachListAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.list_url = reverse("coach:list")

        # Define coach types using the choices
        self.coach_type_offline = Coach.TYPE_OFFLINE
        self.coach_type_online = Coach.TYPE_ONLINE

        # Create coaches
        self.coach1 = CoachFactory(
            first_name="Coach",
            last_name="One",
            type=self.coach_type_offline,
            website="https://coachone.com",
            email="coach1@example.com",
            phone_number="+1234567890",
            location="New York",
            verification_status="verified",
            experience_level="expert",
        )

        self.coach2 = CoachFactory(
            first_name="Coach",
            last_name="Two",
            type=self.coach_type_online,
            website="https://coachtwo.com",
            email="coach2@example.com",
            phone_number="+0987654321",
            location="Los Angeles",
            verification_status="not verified",
            experience_level="beginner",
        )

        self.coach3 = CoachFactory(
            first_name="Coach",
            last_name="Three",
            type=self.coach_type_offline,
            website="https://coachthree.com",
            email="coach3@example.com",
            phone_number="+1122334455",
            location="Chicago",
            verification_status="verified plus",
            experience_level="intermediate",
        )

    def test_list_coaches_success(self):
        """Test successful retrieval of coaches list"""
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "count" in data
        assert "results" in data
        assert data["count"] == 3  # noqa: PLR2004

        # Check first result has expected fields
        first_coach = data["results"][0]
        assert "id" in first_coach
        assert "first_name" in first_coach
        assert "last_name" in first_coach
        assert "profile_picture" in first_coach
        assert "cover_image" in first_coach
        assert "type" in first_coach
        assert "company" in first_coach  # Check company field
        assert "website" in first_coach
        assert "email" in first_coach
        assert "phone_number" in first_coach
        assert "location" in first_coach
        assert "category" in first_coach
        assert "subcategory" in first_coach
        assert "verification_status" in first_coach
        assert "experience_level" in first_coach
        assert "is_saved" in first_coach
        assert "is_saved_uuid" in first_coach
        assert "is_claimable" in first_coach
        assert "avg_rating" in first_coach
        assert "review_count" in first_coach
        assert "total_events" in first_coach
        assert "total_products" in first_coach

    def test_avg_rating_and_review_count_in_response(self):
        """Test that avg_rating and review_count are present in the API response"""
        # Expected values
        expected_rating = 4.5  # Average of 5 and 4
        expected_review_count = 2  # Two approved reviews
        default_rating = 0.0
        default_review_count = 0

        # Create reviews for coach1 with specific dates to ensure consistent ordering
        CoachReviewFactory(
            coach=self.coach1,
            rating=5,
            comment="Great coach!",
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-01",  # Set a specific date
        )
        CoachReviewFactory(
            coach=self.coach1,
            rating=4,
            comment="Very helpful!",
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-02",  # Set a specific date
        )

        # Create a pending review that shouldn't affect the averages
        CoachReviewFactory(
            coach=self.coach1,
            rating=1,
            comment="Pending review",
            status=CoachReview.STATUS_PENDING,
            date="2025-01-03",  # Set a specific date
        )

        # Get all coaches with consistent ordering by name
        response = self.client.get(f"{self.list_url}?ordering=name")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Convert results to a dictionary for easier lookup using full name
        coaches_data = {
            f"{coach['first_name']} {coach['last_name']}": coach
            for coach in data["results"]
        }

        # Verify coach1 data (we know its name is "Coach One")
        coach1_data = coaches_data["Coach One"]
        assert "avg_rating" in coach1_data
        assert "review_count" in coach1_data
        assert "company" in coach1_data  # Check company field
        assert coach1_data["avg_rating"] == expected_rating
        assert coach1_data["review_count"] == expected_review_count

        # Verify coach2 data (we know its name is "Coach Two")
        coach2_data = coaches_data["Coach Two"]
        assert "avg_rating" in coach2_data
        assert "review_count" in coach2_data
        assert "company" in coach2_data  # Check company field
        assert coach2_data["avg_rating"] == default_rating
        assert coach2_data["review_count"] == default_review_count

    def test_pagination(self):
        """Test pagination functionality"""
        # Create 8 more coaches to have a total of 11 (exceeding default page size of 10)  # noqa: E501
        for _ in range(8):
            CoachFactory(type=self.coach_type_offline)

        response = self.client.get(self.list_url)
        data = response.json()

        assert data["count"] == 11  # noqa: PLR2004
        assert len(data["results"]) == 10  # Default page size  # noqa: PLR2004
        assert data["next"] is not None  # Should have next page

        # Get second page
        response = self.client.get(data["next"])
        data = response.json()

        assert len(data["results"]) == 1  # One coach on second page

    def test_filtering_by_type(self):
        """Test filtering coaches by type"""
        response = self.client.get(f"{self.list_url}?type={self.coach_type_offline}")
        data = response.json()

        assert data["count"] == 2  # Two coaches with offline type  # noqa: PLR2004
        assert all(
            coach["type"] == self.coach_type_offline for coach in data["results"]
        )

    def test_filtering_by_verification_status(self):
        """Test filtering coaches by verification status"""
        response = self.client.get(f"{self.list_url}?verification_status=verified")
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["verification_status"] == "verified"

    def test_filtering_by_experience_level(self):
        """Test filtering coaches by experience level"""
        response = self.client.get(f"{self.list_url}?experience_level=beginner")
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["experience_level"] == "beginner"

    def test_filtering_by_category(self):
        """Test filtering coaches by category"""
        # Create categories
        from coach.tests.factories import CategoryFactory

        category1 = CategoryFactory(name="Life Coaching")
        category2 = CategoryFactory(name="Business Coaching")

        # Update coaches with categories
        self.coach1.category = category1
        self.coach1.save()
        self.coach2.category = category2
        self.coach2.save()

        # Test filtering by category ID
        response = self.client.get(f"{self.list_url}?category={category1.id}")
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["category"]["id"] == category1.id
        assert data["results"][0]["category"]["name"] == "Life Coaching"

        # Test filtering by category name
        url = f"{self.list_url}?category__name__icontains=business"
        response = self.client.get(url)
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["category"]["name"] == "Business Coaching"

    def test_filtering_by_subcategory(self):
        """Test filtering coaches by subcategory"""
        # Create subcategories
        from coach.tests.factories import SubCategoryFactory

        subcategory1 = SubCategoryFactory(name="Career Development")
        subcategory2 = SubCategoryFactory(name="Leadership Training")

        # Add subcategories to coaches
        self.coach1.subcategory.add(subcategory1)
        self.coach2.subcategory.add(subcategory2)

        # Test filtering by subcategory ID
        response = self.client.get(f"{self.list_url}?subcategory={subcategory1.id}")
        data = response.json()

        assert data["count"] == 1
        coach_subcategories = [sub["id"] for sub in data["results"][0]["subcategory"]]
        assert subcategory1.id in coach_subcategories

        # Test filtering by subcategory name
        url = f"{self.list_url}?subcategory__name__icontains=leadership"
        response = self.client.get(url)
        data = response.json()

        assert data["count"] == 1
        subcategory_names = [sub["name"] for sub in data["results"][0]["subcategory"]]
        assert "Leadership Training" in subcategory_names

    def test_search_functionality(self):
        """Test search functionality"""
        # Search by last name
        response = self.client.get(f"{self.list_url}?search=Two")
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["last_name"] == "Two"

        # Search by first name
        response = self.client.get(f"{self.list_url}?search=Coach")
        data = response.json()

        assert (
            data["count"] == 3  # noqa: PLR2004
        )  # All coaches have first_name="Coach"  # noqa: PLR2004, RUF100

    def test_ordering_functionality(self):
        """Test ordering functionality"""
        # Order by last_name ascending
        response = self.client.get(f"{self.list_url}?ordering=last_name")
        data = response.json()

        last_names = [coach["last_name"] for coach in data["results"]]
        assert last_names == sorted(last_names)

        # Order by last_name descending
        response = self.client.get(f"{self.list_url}?ordering=-last_name")
        data = response.json()

        last_names = [coach["last_name"] for coach in data["results"]]
        assert last_names == sorted(last_names, reverse=True)

    def test_custom_page_size(self):
        """Test custom page size parameter"""
        response = self.client.get(f"{self.list_url}?page_size=2")
        data = response.json()

        assert len(data["results"]) == 2  # noqa: PLR2004
        assert data["next"] is not None

    def test_empty_search_results(self):
        """Test that searching for non-existent coach returns empty results but 200 status"""  # noqa: E501
        response = self.client.get(f"{self.list_url}?search=NonExistentCoach")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["count"] == 0
        assert len(data["results"]) == 0

    def test_multiple_filters(self):
        """Test filtering by multiple parameters simultaneously"""
        # Filter by both type and experience level
        response = self.client.get(
            f"{self.list_url}?type={self.coach_type_offline}&experience_level=expert",
        )
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["type"] == self.coach_type_offline
        assert data["results"][0]["experience_level"] == "expert"
        assert data["results"][0]["first_name"] == "Coach"
        assert data["results"][0]["last_name"] == "One"

        # Optionally, add a check for company in filtered results
        for coach in data["results"]:
            assert "company" in coach

    def test_invalid_filter_parameters(self):
        """Test behavior with invalid filter parameters"""
        # Test with invalid type value
        response = self.client.get(f"{self.list_url}?type=invalid_type")

        # Should return 400 status
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Test with invalid experience level
        response = self.client.get(f"{self.list_url}?experience_level=invalid_level")

        # Should return 400 status
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # TODO: Add test for filtering by location (exact match) and partial match
    # def test_filtering_by_location_contains(self):
    #     """Test filtering coaches by partial location match"""
    #     response = self.client.get(f"{self.list_url}?location__contains=York")  # noqa: E501, ERA001
    #     data = response.json()  # noqa: ERA001

    #     assert data["count"] == 1  # noqa: ERA001
    #     assert "York" in data["results"][0]["location"]  # noqa: ERA001

    def test_combined_search_and_filter(self):
        """Test combining search with specific filters"""
        response = self.client.get(
            f"{self.list_url}?search=Coach&type={self.coach_type_offline}",
        )
        data = response.json()

        assert data["count"] == 2  # noqa: PLR2004
        assert all(
            coach["type"] == self.coach_type_offline for coach in data["results"]
        )

    def test_ordering_by_rating_and_reviews(self):
        """Test ordering coaches by average rating and review count"""
        # Create reviews with different ratings for each coach
        # Coach1: 2 reviews, avg 4.5
        CoachReviewFactory(
            coach=self.coach1,
            rating=5,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-01",
        )
        CoachReviewFactory(
            coach=self.coach1,
            rating=4,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-02",
        )

        # Coach2: 3 reviews, avg 4.0
        CoachReviewFactory(
            coach=self.coach2,
            rating=5,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-01",
        )
        CoachReviewFactory(
            coach=self.coach2,
            rating=4,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-02",
        )
        CoachReviewFactory(
            coach=self.coach2,
            rating=3,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-03",
        )

        # Coach3: 1 review, avg 5.0
        CoachReviewFactory(
            coach=self.coach3,
            rating=5,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-01",
        )

        # Test sorting by average rating ascending
        response = self.client.get(f"{self.list_url}?ordering=avg_rating")
        data = response.json()
        ratings = [coach["avg_rating"] for coach in data["results"]]
        assert ratings == sorted(ratings)  # Should be [4.0, 4.5, 5.0]

        # Test sorting by average rating descending
        response = self.client.get(f"{self.list_url}?ordering=-avg_rating")
        data = response.json()
        ratings = [coach["avg_rating"] for coach in data["results"]]
        assert ratings == sorted(ratings, reverse=True)  # Should be [5.0, 4.5, 4.0]

        # Test sorting by review count ascending
        response = self.client.get(f"{self.list_url}?ordering=review_count")
        data = response.json()
        review_counts = [coach["review_count"] for coach in data["results"]]
        assert review_counts == sorted(review_counts)  # Should be [1, 2, 3]

        # Test sorting by review count descending
        response = self.client.get(f"{self.list_url}?ordering=-review_count")
        data = response.json()
        review_counts = [coach["review_count"] for coach in data["results"]]
        # Should be [3, 2, 1]
        assert review_counts == sorted(review_counts, reverse=True)

        # Test sorting by rating and then review count
        response = self.client.get(f"{self.list_url}?ordering=avg_rating,review_count")
        data = response.json()
        coaches = [(c["avg_rating"], c["review_count"]) for c in data["results"]]
        assert coaches == sorted(coaches)  # Should sort first by rating then by reviews

    def test_filtering_by_multiple_categories(self):
        """Test filtering coaches by multiple categories"""
        # Create categories
        from coach.tests.factories import CategoryFactory

        category1 = CategoryFactory(name="Life Coaching")
        category2 = CategoryFactory(name="Business Coaching")
        category3 = CategoryFactory(name="Health Coaching")

        # Update coaches with categories
        self.coach1.category = category1
        self.coach1.save()
        self.coach2.category = category2
        self.coach2.save()
        self.coach3.category = category3
        self.coach3.save()

        # Test filtering by multiple category IDs using comma-separated values
        url = f"{self.list_url}?category={category1.id},{category2.id}"
        response = self.client.get(url)
        data = response.json()

        expected_count = 2
        assert data["count"] == expected_count
        category_ids = [coach["category"]["id"] for coach in data["results"]]
        assert category1.id in category_ids
        assert category2.id in category_ids
        assert category3.id not in category_ids

        # Test filtering by multiple category names
        url = f"{self.list_url}?category__name__in=Life Coaching,Business Coaching"
        response = self.client.get(url)
        data = response.json()

        assert data["count"] == expected_count
        category_names = [coach["category"]["name"] for coach in data["results"]]
        assert "Life Coaching" in category_names
        assert "Business Coaching" in category_names
        assert "Health Coaching" not in category_names

    def test_filtering_by_multiple_subcategories(self):
        """Test filtering coaches by multiple subcategories"""
        # Create subcategories
        from coach.tests.factories import SubCategoryFactory

        subcategory1 = SubCategoryFactory(name="Career Development")
        subcategory2 = SubCategoryFactory(name="Leadership Training")
        subcategory3 = SubCategoryFactory(name="Personal Growth")
        subcategory4 = SubCategoryFactory(name="Team Building")

        # Add subcategories to coaches
        self.coach1.subcategory.add(subcategory1, subcategory2)
        self.coach2.subcategory.add(subcategory3)
        self.coach3.subcategory.add(subcategory4)

        # Test filtering by multiple subcategory IDs using comma-separated values
        url = f"{self.list_url}?subcategory={subcategory1.id},{subcategory3.id}"
        response = self.client.get(url)
        data = response.json()

        expected_count = 2
        assert data["count"] == expected_count
        # Verify coach1 has subcategory1
        coach1_found = False
        coach2_found = False
        for coach in data["results"]:
            subcategory_ids = [sub["id"] for sub in coach["subcategory"]]
            if subcategory1.id in subcategory_ids:
                coach1_found = True
            if subcategory3.id in subcategory_ids:
                coach2_found = True
        assert coach1_found
        assert coach2_found

        # Test filtering by multiple subcategory names
        url = (
            f"{self.list_url}?subcategory__name__in=Career Development,Personal Growth"
        )
        response = self.client.get(url)
        data = response.json()

        assert data["count"] == expected_count
        subcategory_names_found = []
        for coach in data["results"]:
            subcategory_names_found.extend(
                [subcategory["name"] for subcategory in coach["subcategory"]],
            )
        assert "Career Development" in subcategory_names_found
        assert "Personal Growth" in subcategory_names_found

    def test_filtering_by_multiple_categories_and_subcategories(self):
        """Test filtering coaches by multiple categories AND subcategories combined"""
        # Create categories and subcategories
        from coach.tests.factories import CategoryFactory
        from coach.tests.factories import SubCategoryFactory

        category1 = CategoryFactory(name="Life Coaching")
        category2 = CategoryFactory(name="Business Coaching")

        subcategory1 = SubCategoryFactory(name="Career Development")
        subcategory2 = SubCategoryFactory(name="Leadership Training")

        # Set up coaches with specific combinations
        self.coach1.category = category1
        self.coach1.save()
        self.coach1.subcategory.add(subcategory1)

        self.coach2.category = category2
        self.coach2.save()
        self.coach2.subcategory.add(subcategory2)

        self.coach3.category = category1
        self.coach3.save()
        self.coach3.subcategory.add(subcategory2)

        # Test filtering by specific category and subcategory combination
        url = f"{self.list_url}?category={category1.id}&subcategory={subcategory1.id}"
        response = self.client.get(url)
        data = response.json()

        # Should only return coach1 (category1 + subcategory1)
        assert data["count"] == 1
        coach = data["results"][0]
        assert coach["category"]["id"] == category1.id
        subcategory_ids = [sub["id"] for sub in coach["subcategory"]]
        assert subcategory1.id in subcategory_ids

        # Test filtering by multiple categories and multiple subcategories
        url = (
            f"{self.list_url}?category={category1.id},{category2.id}"
            f"&subcategory={subcategory1.id},{subcategory2.id}"
        )
        response = self.client.get(url)
        data = response.json()

        # Should return coaches that have any of the specified categories
        # AND any of the specified subcategories
        assert data["count"] >= 1  # At least coach1 should match

    def test_filtering_by_avg_rating(self):
        """Test filtering coaches by average rating"""
        # Constants for test ratings
        rating_perfect = 5.0
        rating_good = 4.5
        rating_average = 4.0
        rating_highest_threshold = 5.5

        # Create reviews with different ratings for each coach
        # Coach1: 2 reviews, avg 4.5 (ratings: 5, 4)
        CoachReviewFactory(
            coach=self.coach1,
            rating=5,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-01",
        )
        CoachReviewFactory(
            coach=self.coach1,
            rating=4,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-02",
        )

        # Coach2: 3 reviews, avg 4.0 (ratings: 5, 4, 3)
        CoachReviewFactory(
            coach=self.coach2,
            rating=5,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-01",
        )
        CoachReviewFactory(
            coach=self.coach2,
            rating=4,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-02",
        )
        CoachReviewFactory(
            coach=self.coach2,
            rating=3,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-03",
        )

        # Coach3: 1 review, avg 5.0 (rating: 5)
        CoachReviewFactory(
            coach=self.coach3,
            rating=5,
            status=CoachReview.STATUS_APPROVED,
            date="2025-01-01",
        )

        # Test filtering by exact rating (should match coach3 with 5.0)
        response = self.client.get(f"{self.list_url}?avg_rating={rating_perfect}")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["avg_rating"] == rating_perfect

        # Test filtering by minimum rating (should get coaches with rating >= 4.5)
        response = self.client.get(f"{self.list_url}?avg_rating_min={rating_good}")
        data = response.json()
        expected_count = 2  # coach1 (4.5) and coach3 (5.0)
        assert data["count"] == expected_count
        ratings = [coach["avg_rating"] for coach in data["results"]]
        assert all(rating >= rating_good for rating in ratings)

        # Test filtering by maximum rating (should get coaches with rating <= 4.0)
        response = self.client.get(f"{self.list_url}?avg_rating_max={rating_average}")
        data = response.json()
        assert data["count"] == 1  # coach2 (4.0)
        ratings = [coach["avg_rating"] for coach in data["results"]]
        assert all(rating <= rating_average for rating in ratings)

        # Test filtering by rating range (should get coaches with 4.0 <= rating <= 4.5)
        url = (
            f"{self.list_url}?avg_rating_min={rating_average}"
            f"&avg_rating_max={rating_good}"
        )
        response = self.client.get(url)
        data = response.json()
        expected_range_count = 2  # coach1 (4.5) and coach2 (4.0)
        assert data["count"] == expected_range_count
        ratings = [coach["avg_rating"] for coach in data["results"]]
        assert all(rating_average <= rating <= rating_good for rating in ratings)

        # Test filtering with no matches
        url = f"{self.list_url}?avg_rating_min={rating_highest_threshold}"
        response = self.client.get(url)
        data = response.json()
        assert data["count"] == 0

    def test_is_saved_field_for_authenticated_user(self):
        """Test that is_saved field correctly indicates if coach is saved by user"""
        from coach.tests.factories import SavedCoachFactory
        from core.users.tests.factories import UserFactory

        # Create a user and authenticate
        user = UserFactory()
        self.client.force_login(user)

        # Save one of the coaches for this user
        saved_coach = SavedCoachFactory(user=user, coach=self.coach1)

        # Make request to list API
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        coaches_data = {coach["id"]: coach for coach in data["results"]}

        # Check that saved coach has is_saved=True and correct is_saved_uuid
        assert "is_saved" in coaches_data[self.coach1.id]
        assert "is_saved_uuid" in coaches_data[self.coach1.id]
        assert coaches_data[self.coach1.id]["is_saved"] is True
        assert coaches_data[self.coach1.id]["is_saved_uuid"] == str(saved_coach.uuid)

        # Check that non-saved coaches have is_saved=False and is_saved_uuid=None
        assert coaches_data[self.coach2.id]["is_saved"] is False
        assert coaches_data[self.coach2.id]["is_saved_uuid"] is None
        assert coaches_data[self.coach3.id]["is_saved"] is False
        assert coaches_data[self.coach3.id]["is_saved_uuid"] is None

    def test_is_saved_field_for_unauthenticated_user(self):
        """Test that is_saved field is False for unauthenticated users"""
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        # All coaches should have is_saved=False and is_saved_uuid=None for
        # unauthenticated users
        for coach in data["results"]:
            assert "is_saved" in coach
            assert "is_saved_uuid" in coach
            assert coach["is_saved"] is False
            assert coach["is_saved_uuid"] is None

    def test_is_claimable_field_in_response(self):
        """Test that is_claimable field is present and correct in response"""
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        # Check that all coaches have is_claimable field
        for coach in data["results"]:
            assert "is_claimable" in coach
            # Since all test coaches have users, they should not be claimable
            assert coach["is_claimable"] is False

    def test_is_saved_uuid_field_functionality(self):
        """Test comprehensive functionality of is_saved_uuid field"""
        from coach.tests.factories import SavedCoachFactory
        from core.users.tests.factories import UserFactory

        # Create two different users
        user1 = UserFactory()
        user2 = UserFactory()

        # Create saved coach records for different users
        saved_coach1 = SavedCoachFactory(user=user1, coach=self.coach1)
        saved_coach2 = SavedCoachFactory(user=user2, coach=self.coach2)

        # Test with user1 authentication
        self.client.force_login(user1)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        coaches_data = {coach["id"]: coach for coach in data["results"]}

        # User1 should see their saved coach with correct UUID
        assert coaches_data[self.coach1.id]["is_saved"] is True
        assert coaches_data[self.coach1.id]["is_saved_uuid"] == str(saved_coach1.uuid)

        # User1 should not see coach2 as saved (different user)
        assert coaches_data[self.coach2.id]["is_saved"] is False
        assert coaches_data[self.coach2.id]["is_saved_uuid"] is None

        # Coach3 is not saved by anyone
        assert coaches_data[self.coach3.id]["is_saved"] is False
        assert coaches_data[self.coach3.id]["is_saved_uuid"] is None

        # Test with user2 authentication
        self.client.force_login(user2)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        coaches_data = {coach["id"]: coach for coach in data["results"]}

        # User2 should not see coach1 as saved (different user)
        assert coaches_data[self.coach1.id]["is_saved"] is False
        assert coaches_data[self.coach1.id]["is_saved_uuid"] is None

        # User2 should see their saved coach with correct UUID
        assert coaches_data[self.coach2.id]["is_saved"] is True
        assert coaches_data[self.coach2.id]["is_saved_uuid"] == str(saved_coach2.uuid)

        # Coach3 is still not saved by anyone
        assert coaches_data[self.coach3.id]["is_saved"] is False
        assert coaches_data[self.coach3.id]["is_saved_uuid"] is None

        # Test after logout (unauthenticated)
        self.client.logout()
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # All coaches should show as not saved for unauthenticated users
        for coach in data["results"]:
            assert coach["is_saved"] is False
            assert coach["is_saved_uuid"] is None
