from django.db import models


class MetaContent(models.Model):
    """
    Model to store content for the home page.
    Attributes:
        title (CharField): Title of the content.
        content (TextField): Detailed content.
        created_at (DateTimeField): Timestamp when the content was created.
        updated_at (DateTimeField): Timestamp when the content was last updated.
    """

    meta_title = models.CharField(max_length=64, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    link_canonical = models.URLField(blank=True)
    schema = models.TextField(blank=True)
    site_map = models.TextField(blank=True)
    web_page = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.web_page
