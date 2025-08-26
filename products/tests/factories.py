from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from factory import Faker
from factory import SubFactory
from factory import post_generation
from factory.django import DjangoModelFactory
from PIL import Image

from coach.tests.factories import CoachFactory
from products.models import Product
from products.models import ProductCategory
from products.models import ProductType
from products.models import SavedProduct


def create_test_image(filename="product.jpg", size=(100, 100), color="blue"):
    """Helper function to create test image files"""
    image_file = BytesIO()
    image = Image.new("RGB", size=size, color=color)
    image.save(image_file, "JPEG")
    image_file.seek(0)

    return SimpleUploadedFile(
        name=filename,
        content=image_file.read(),
        content_type="image/jpeg",
    )


class ProductCategoryFactory(DjangoModelFactory):
    """Factory for the ProductCategory model."""

    name = Faker("word")
    description = Faker("paragraph")

    class Meta:
        model = ProductCategory
        django_get_or_create = ["name"]


class ProductTypeFactory(DjangoModelFactory):
    """Factory for the ProductType model."""

    name = Faker("word")
    description = Faker("paragraph")

    class Meta:
        model = ProductType
        django_get_or_create = ["name"]


class ProductFactory(DjangoModelFactory):
    """Factory for the Product model."""

    name = Faker("catch_phrase")
    description = Faker("paragraph")
    price = Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    category = SubFactory(ProductCategoryFactory)
    product_type = SubFactory(ProductTypeFactory)
    language = Faker("random_element", elements=["en", "es", "fr", "de", "it"])
    coach = SubFactory(CoachFactory)
    is_featured = False
    external_url = Faker("url")
    release_date = Faker("date_this_year")
    ct_id = Faker("uuid4")
    product_id = Faker("uuid4")

    @post_generation
    def image(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.image = extracted
        else:
            self.image = create_test_image("product.jpg")

    class Meta:
        model = Product
        django_get_or_create = ["name"]


class SavedProductFactory(DjangoModelFactory):
    """
    Factory for creating test instances of SavedProduct model.
    This factory creates SavedProduct instances with relationships to users and products.
    It uses get_or_create to avoid duplicate saved products for the same user and product.
    Attributes:
        user: The user who saved the product.
        product: The product that was saved.
    """  # noqa: E501

    user = SubFactory("users.tests.factories.UserFactory")
    product = SubFactory(ProductFactory)

    class Meta:
        model = SavedProduct
        django_get_or_create = ["user", "product"]


class UserWithSavedProductsFactory(DjangoModelFactory):
    """
    Factory for creating User instances with associated saved products.
    This factory creates an active user with a random username and email,
    and associates a specified number of products as "saved" for this user.
    Attributes:
        username: A randomly generated username using Faker.
        email: A randomly generated email using Faker.
        is_active: Set to True by default.
    Usage:
        # Create a user with the default 10 saved products
        user = UserWithSavedProductsFactory()
        # Create a user with a specific number of saved products
        user_with_5_products = UserWithSavedProductsFactory(saved_products=5)
        # Create a user with no saved products
        user_without_products = UserWithSavedProductsFactory(saved_products=0)
    """

    class Meta:
        model = "users.User"  # Use the string reference to avoid circular imports

    username = Faker("user_name")
    email = Faker("email")
    is_active = True

    @post_generation
    def saved_products(self, create, extracted, **kwargs):
        if not create:
            return

        # Default to 10 saved products if not specified
        count = extracted if extracted is not None else 10

        # Create count number of products and save them for this user
        for _ in range(count):
            product = ProductFactory()
            SavedProductFactory(user=self, product=product)
