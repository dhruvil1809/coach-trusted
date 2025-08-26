import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from coach.models import SocialMediaLink
from coach.tests.factories import CoachFactory
from coach.tests.factories import SocialMediaLinkFactory


class TestSocialMediaLink(TestCase):
    def setUp(self):
        self.coach = CoachFactory()

    def test_social_media_link_creation(self):
        """Test that SocialMediaLink can be created with a coach"""
        social_media_link = SocialMediaLinkFactory(coach=self.coach)

        assert social_media_link.coach == self.coach
        assert social_media_link.uuid is not None
        assert social_media_link.created_at is not None
        assert social_media_link.updated_at is not None

    def test_social_media_link_creation_with_specific_links(self):
        """Test creation with specific social media links"""
        social_media_link = SocialMediaLinkFactory(
            coach=self.coach,
            instagram="https://instagram.com/testcoach",
            facebook="https://facebook.com/testcoach",
            linkedin="https://linkedin.com/in/testcoach",
            youtube="https://youtube.com/c/testcoach",
            tiktok="https://tiktok.com/@testcoach",
            x="https://x.com/testcoach",
            trustpilot="https://trustpilot.com/review/testcoach",
            google="https://google.com/maps/testcoach",
            provexpert="https://provexpert.com/testcoach",
        )

        assert social_media_link.instagram == "https://instagram.com/testcoach"
        assert social_media_link.facebook == "https://facebook.com/testcoach"
        assert social_media_link.linkedin == "https://linkedin.com/in/testcoach"
        assert social_media_link.youtube == "https://youtube.com/c/testcoach"
        assert social_media_link.tiktok == "https://tiktok.com/@testcoach"
        assert social_media_link.x == "https://x.com/testcoach"
        assert social_media_link.trustpilot == "https://trustpilot.com/review/testcoach"
        assert social_media_link.google == "https://google.com/maps/testcoach"
        assert social_media_link.provexpert == "https://provexpert.com/testcoach"

    def test_social_media_link_creation_with_empty_links(self):
        """Test creation with empty/blank social media links"""
        social_media_link = SocialMediaLinkFactory(
            coach=self.coach,
            instagram="",
            facebook="",
            linkedin="",
            youtube="",
            tiktok="",
            x="",
            trustpilot="",
            google="",
            provexpert="",
        )

        assert social_media_link.instagram == ""
        assert social_media_link.facebook == ""
        assert social_media_link.linkedin == ""
        assert social_media_link.youtube == ""
        assert social_media_link.tiktok == ""
        assert social_media_link.x == ""
        assert social_media_link.trustpilot == ""
        assert social_media_link.google == ""
        assert social_media_link.provexpert == ""

    def test_string_representation(self):
        """Test string representation of SocialMediaLink model"""
        social_media_link = SocialMediaLinkFactory(coach=self.coach)
        expected_str = (
            f"{self.coach.first_name} {self.coach.last_name} Social Media Links".strip()
        )

        assert str(social_media_link) == expected_str

    def test_string_representation_with_coach_having_only_first_name(self):
        """Test string representation when coach has only first name"""
        coach_with_first_name_only = CoachFactory(first_name="John", last_name="")
        social_media_link = SocialMediaLinkFactory(coach=coach_with_first_name_only)
        expected_str = "John  Social Media Links"

        assert str(social_media_link) == expected_str

    def test_one_to_one_relationship_with_coach(self):
        """Test that SocialMediaLink has a one-to-one relationship with Coach"""
        # Create first social media link
        SocialMediaLinkFactory(coach=self.coach)

        # Try to create another social media link for the same coach
        with pytest.raises(IntegrityError):
            SocialMediaLinkFactory(coach=self.coach)

    def test_coach_deletion_cascades_to_social_media_link(self):
        """Test that deleting a coach also deletes associated social media link"""
        social_media_link = SocialMediaLinkFactory(coach=self.coach)
        social_media_link_id = social_media_link.id

        # Delete the coach
        self.coach.delete()

        # Verify social media link is also deleted
        assert not SocialMediaLink.objects.filter(id=social_media_link_id).exists()

    def test_coach_social_media_links_related_name(self):
        """Test that coach can access social media link through related name"""
        social_media_link = SocialMediaLinkFactory(coach=self.coach)

        # Access through related name
        assert self.coach.social_media_links == social_media_link

    def test_uuid_field_is_unique(self):
        """Test that UUID field is unique and auto-generated"""
        social_media_link1 = SocialMediaLinkFactory()
        social_media_link2 = SocialMediaLinkFactory()

        assert social_media_link1.uuid != social_media_link2.uuid
        assert social_media_link1.uuid is not None
        assert social_media_link2.uuid is not None

    def test_verbose_names(self):
        """Test verbose names are set correctly"""
        meta = SocialMediaLink._meta  # noqa: SLF001

        assert meta.verbose_name == "Social Media Link"
        assert meta.verbose_name_plural == "Social Media Links"

    def test_url_field_validation(self):
        """Test that URL fields validate proper URLs"""
        # Test with invalid URL
        social_media_link = SocialMediaLink(
            coach=self.coach,
            instagram="not-a-valid-url",
        )
        with pytest.raises(ValidationError):
            social_media_link.full_clean()  # This triggers validation

    def test_url_field_allows_blank(self):
        """Test that URL fields allow blank values"""
        social_media_link = SocialMediaLink(
            coach=self.coach,
            instagram="",  # Blank value
            facebook="",
            linkedin="",
            youtube="",
            tiktok="",
            x="",
            trustpilot="",
            google="",
            provexpert="",
        )

        # This should not raise any validation errors
        social_media_link.full_clean()
        social_media_link.save()

        assert social_media_link.id is not None

    def test_help_text_attributes(self):
        """Test that help text is set correctly for URL fields"""
        fields = SocialMediaLink._meta.get_fields()  # noqa: SLF001
        field_help_texts = {
            field.name: getattr(field, "help_text", "")
            for field in fields
            if hasattr(field, "help_text")
        }

        expected_help_texts = {
            "instagram": "Instagram profile link",
            "facebook": "Facebook profile link",
            "linkedin": "LinkedIn profile link",
            "youtube": "YouTube channel link",
            "tiktok": "TikTok profile link",
            "x": "X (formerly Twitter) profile link",
            "trustpilot": "Trustpilot profile link",
            "google": "Google profile link",
            "provexpert": "ProvExpert profile link",
        }

        for field_name, expected_help_text in expected_help_texts.items():
            assert field_help_texts.get(field_name) == expected_help_text
