import re

from factory import Faker
from factory import LazyAttribute
from factory.django import DjangoModelFactory
from faker import Faker as FakerInstance

from inquiries.models import GeneralInquiry


class GeneralInquiryFactory(DjangoModelFactory):
    """Factory for the GeneralInquiry model."""

    subject = Faker("sentence")
    message = Faker("paragraph")
    business_name = Faker("company")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = LazyAttribute(
        lambda o: f"{o.first_name.lower()}.{o.last_name.lower()}@example.com",
    )
    country = Faker("country")
    phone = LazyAttribute(
        lambda o: re.sub(r"\D", "", FakerInstance().phone_number())[:15],
    )

    class Meta:
        model = GeneralInquiry
