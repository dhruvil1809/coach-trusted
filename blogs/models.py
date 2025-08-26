from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:  # noqa: DJ012
        verbose_name_plural = "Categories"


class Post(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
    ]

    title = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=1000, unique=True, blank=True)
    image = models.ImageField(
        upload_to="posts/images/",
        blank=True,
        null=True,
        help_text="Image for the post. Optional, but recommended for better visibility.",  # noqa: E501
    )

    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        help_text="Status of the post. 'Draft' means it is not published yet, 'Published' means it is visible to users.",  # noqa: E501
    )

    content = CKEditor5Field()
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="posts",
        help_text="Category to which this post belongs.",
        verbose_name="Category",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
