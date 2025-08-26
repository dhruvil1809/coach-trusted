from django.db import models


class GeneralInquiry(models.Model):
    subject = models.CharField(max_length=1000)
    message = models.TextField()
    business_name = models.CharField(max_length=1000)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    country = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "General Inquiry"
        verbose_name_plural = "General Inquiries"

    def __str__(self):
        return f"{self.subject} - {self.business_name} ({self.first_name} {self.last_name})"  # noqa: E501
