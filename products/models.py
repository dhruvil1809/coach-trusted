import uuid

from django.db import models
from django.utils.text import slugify

from coach.models import Coach
from core.users.models import User


def get_product_image_upload_path(instance, filename):
    """
    Generates a unique upload path for product images.
    This function creates a unique filename for product images using UUID4 and
    preserves the original file extension. The resulting path will be in the
    format 'products/images/{uuid}.{extension}'.
    Parameters:
        instance: The model instance the file is attached to.
        filename (str): Original filename of the uploaded file.
    Returns:
        str: A unique file path for the uploaded product image.
    """

    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"products/images/{filename}"


def get_product_media_upload_path(instance, filename):
    """
    Generate a unique file path for uploaded product media.
    This function creates a unique filename for uploaded media files associated with products
    by using a UUID and preserving the original file extension.
    Args:
        instance: The model instance where the file is being attached to.
        filename (str): The original filename of the uploaded file.
    Returns:
        str: A path string in the format 'products/media/{uuid}.{extension}' where:
            - uuid: A randomly generated UUID as a hexadecimal string
            - extension: The original file extension
    Example:
        >>> get_product_media_upload_path(None, "image.jpg")
        'products/media/3f2504e0-4f89-11d3-9a0c-0305e82c3301.jpg'
    """  # noqa: E501

    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"products/media/{filename}"


class Product(models.Model):
    """
    Model representing a product.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this product",
    )

    ct_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique identifier for the product in the Coach Trusted system",
    )
    product_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique identifier for the product",
    )
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField(
        help_text="The date when the product was released",
        blank=True,
        null=True,
    )
    image = models.ImageField(upload_to=get_product_image_upload_path)
    category = models.ForeignKey(
        "ProductCategory",
        on_delete=models.RESTRICT,
        related_name="products",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    external_url = models.URLField(
        blank=True,
        help_text="External URL for the product",
    )

    slug = models.SlugField(
        max_length=500,
        unique=True,
        help_text="Unique slug for this product",
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Indicates if the product is featured",
    )
    product_type = models.ForeignKey(
        "ProductType",
        on_delete=models.RESTRICT,
        related_name="products",
        help_text="Type of the product",
        null=True,
        blank=True,
    )
    language = models.CharField(
        max_length=10,
        choices=[
            ("en", "English"),
            ("es", "Spanish"),
            ("fr", "French"),
            ("de", "German"),
            ("it", "Italian"),
        ],
        default="en",
        help_text="Language of the product",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Override save method to ensure the slug is unique and based on the product name.
        """
        if not self.slug:
            self.slug = f"{slugify(self.name)}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class ProductMedia(models.Model):
    """
    Model representing media associated with a product.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="media")
    media_file = models.FileField(upload_to=get_product_media_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Product Media"
        verbose_name_plural = "Product Media"

    def __str__(self):
        return f"{self.product.name} - {self.media_file.name}"


class ProductCategory(models.Model):
    """
    Model representing a category for products.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this category",
    )

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="Unique slug for this category",
    )
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Override save method to ensure the slug is unique and based on the category name.
        """  # noqa: E501
        if not self.slug:
            self.slug = f"{slugify(self.name)}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class SavedProduct(models.Model):
    """
    Model representing a saved product for a user.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this saved product",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_products",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="saved_products",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Saved Product"
        verbose_name_plural = "Saved Products"
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} saved {self.product.name}"


class ProductType(models.Model):
    """
    Model representing a type of product.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this product type",
    )

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
