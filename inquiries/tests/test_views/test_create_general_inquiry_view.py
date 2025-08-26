from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from inquiries.models import GeneralInquiry


class TestCreateGeneralInquiryView(APITestCase):
    def setUp(self):
        self.url = reverse("inquiries:create-general-inquiry")
        self.valid_payload = {
            "subject": "Test Subject",
            "message": "Test message.",
            "business_name": "Test Business",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "country": "Testland",
            "phone": "1234567890",
        }

    def test_create_general_inquiry_success(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert GeneralInquiry.objects.filter(email="john.doe@example.com").exists()

    def test_create_general_inquiry_invalid(self):
        invalid_payload = self.valid_payload.copy()
        invalid_payload.pop("email")
        response = self.client.post(self.url, invalid_payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
