from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from factory import Faker
from factory import SubFactory
from factory import post_generation
from factory.django import DjangoModelFactory
from PIL import Image

from coach.models import Category
from coach.models import ClaimCoachRequest
from coach.models import Coach
from coach.models import CoachMedia
from coach.models import CoachReview
from coach.models import SavedCoach
from coach.models import SocialMediaLink
from coach.models import SubCategory
from core.users.tests.factories import UserFactory


def create_test_image(filename="test.jpg", size=(100, 100), color="blue"):
    """Helper function to create test image files"""
    image_file = BytesIO()
    image = Image.new("RGB", size, color)
    image.save(image_file, "JPEG" if filename.endswith(".jpg") else "PNG")
    image_file.seek(0)
    return SimpleUploadedFile(
        filename,
        image_file.read(),
        content_type="image/jpeg" if filename.endswith(".jpg") else "image/png",
    )


def create_test_video(filename="test.mp4"):
    """Helper function to create test video files"""
    # Create a minimal fake video file content
    video_content = b"fake video content for testing"
    return SimpleUploadedFile(
        filename,
        video_content,
        content_type="video/mp4",
    )


def create_test_document(filename="test.pdf"):
    """Helper function to create test document files"""
    # Create a minimal fake document file content
    document_content = b"fake document content for testing"
    return SimpleUploadedFile(
        filename,
        document_content,
        content_type="application/pdf",
    )


class CategoryFactory(DjangoModelFactory):
    """Factory for the Category model."""

    name = Faker("word")  # Use a random word instead of sequence
    description = Faker("paragraph")

    class Meta:
        model = Category
        django_get_or_create = ("name",)


class SubCategoryFactory(DjangoModelFactory):
    """Factory for the SubCategory model."""

    name = Faker("word")  # Use a random word instead of sequence
    description = Faker("paragraph")
    category = SubFactory(CategoryFactory)  # Link to a random category

    class Meta:
        model = SubCategory
        django_get_or_create = ("name",)


class CoachFactory(DjangoModelFactory):
    """Factory for the Coach model."""

    user = SubFactory(UserFactory)
    title = Faker("job")  # Add title field
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    type = "offline"  # Default to offline, can be overridden with online when creating
    about = Faker("paragraph")

    company = Faker("company")
    street_no = Faker("building_number")
    zip_code = Faker("postcode")
    city = Faker("city")
    country = Faker("country")
    website = Faker("url")
    email = Faker("email")
    phone_number = Faker("numerify", text="##########")  # 10 digits
    location = Faker("city")
    verification_status = "not verified"
    experience_level = "beginner"
    review_status = Coach.REVIEW_APPROVED  # Default to approved for tests

    # Use a default category name for consistency
    category = SubFactory(CategoryFactory, name="Fitness")

    @post_generation
    def subcategory(self, create, extracted, **kwargs):
        """Add subcategories to the coach (ManyToManyField)."""
        if not create:
            return

        if extracted:
            # If specific subcategories are provided, use them
            for subcategory in extracted:
                self.subcategory.add(subcategory)
        else:
            # By default, create 1-2 predefined subcategories to reduce randomness
            subcategory1 = SubCategoryFactory(name="Personal Training")
            subcategory2 = SubCategoryFactory(name="Nutrition Coaching")
            self.subcategory.add(subcategory1, subcategory2)

    @post_generation
    def profile_picture(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.profile_picture = extracted
        else:
            self.profile_picture = create_test_image("profile.jpg")

    @post_generation
    def cover_image(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.cover_image = extracted
        else:
            self.cover_image = create_test_image("cover.png")

    class Meta:
        model = Coach


class CoachMediaFactory(DjangoModelFactory):
    """Factory for the CoachMedia model."""

    coach = SubFactory(CoachFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Remove file_type logic, always create an image
        kwargs["file"] = create_test_image("coach_media.jpg", size=(200, 150))
        return super()._create(model_class, *args, **kwargs)

    class Meta:
        model = CoachMedia


class ClaimCoachRequestFactory(DjangoModelFactory):
    """Factory for the ClaimCoachRequest model."""

    user = None  # Default to None, can be overridden when creating
    coach = SubFactory(CoachFactory, user=None)  # Create coach with no user by default

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")
    country = Faker("country")
    phone_number = Faker("numerify", text="##########")  # 10 digits

    status = ClaimCoachRequest.STATUS_PENDING  # Default to pending
    rejection_reason = ""
    approval_reason = ""

    class Meta:
        model = ClaimCoachRequest


class CoachReviewFactory(DjangoModelFactory):
    """Factory for the CoachReview model."""

    coach = SubFactory(CoachFactory)
    user = SubFactory(UserFactory)

    rating = Faker("random_int", min=1, max=5)
    comment = Faker("paragraph")
    date = Faker("date_this_year")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")

    status = CoachReview.STATUS_PENDING  # Default to pending
    rejection_reason = ""
    approval_reason = ""

    @post_generation
    def proof_file(self, create, extracted, **kwargs):
        """Generate a test proof file if not provided explicitly."""
        if not create:
            return

        if extracted:
            self.proof_file = extracted
        else:
            # Create a simple text file as proof
            file_content = b"This is a test proof document"
            self.proof_file = SimpleUploadedFile(
                "proof.txt",
                file_content,
                content_type="text/plain",
            )

    class Meta:
        model = CoachReview


class SocialMediaLinkFactory(DjangoModelFactory):
    """Factory for the SocialMediaLink model."""

    coach = SubFactory(CoachFactory)
    instagram = Faker("url")
    facebook = Faker("url")
    linkedin = Faker("url")
    youtube = Faker("url")
    tiktok = Faker("url")
    x = Faker("url")
    trustpilot = Faker("url")
    google = Faker("url")
    provexpert = Faker("url")

    class Meta:
        model = SocialMediaLink


class SavedCoachFactory(DjangoModelFactory):
    """Factory for the SavedCoach model."""

    user = SubFactory(UserFactory)
    coach = SubFactory(CoachFactory)

    class Meta:
        model = SavedCoach
        django_get_or_create = ("user", "coach")  # Ensure user-coach pair is unique
