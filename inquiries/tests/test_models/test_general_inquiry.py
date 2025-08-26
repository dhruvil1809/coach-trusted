from django.test import TestCase

from inquiries.models import GeneralInquiry
from inquiries.tests.factories import GeneralInquiryFactory


class TestGeneralInquiryModel(TestCase):
    def test_general_inquiry_creation(self):
        inquiry = GeneralInquiryFactory()
        assert isinstance(inquiry, GeneralInquiry)
        assert inquiry.pk is not None
        assert inquiry.subject
        assert inquiry.message
        assert inquiry.business_name
        assert inquiry.first_name
        assert inquiry.last_name
        assert inquiry.email
        assert inquiry.country
        assert inquiry.phone
        assert inquiry.created_at is not None

    def test_general_inquiry_str(self):
        inquiry = GeneralInquiryFactory(
            subject="Test Subject",
            business_name="Test Business",
            first_name="John",
            last_name="Doe",
        )
        expected_str = "Test Subject - Test Business (John Doe)"
        assert str(inquiry) == expected_str
