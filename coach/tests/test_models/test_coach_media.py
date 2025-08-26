import tempfile

from django.test import TestCase
from django.test import override_settings

from coach.models import CoachMedia
from coach.tests.factories import CoachFactory
from coach.tests.factories import CoachMediaFactory


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class CoachMediaModelTestCase(TestCase):
    """Test cases for the CoachMedia model."""

    def test_coach_media_creation(self):
        """Test creating a CoachMedia instance."""
        coach_media = CoachMediaFactory()

        assert isinstance(coach_media, CoachMedia)
        assert coach_media.coach is not None
        assert coach_media.file is not None
        assert coach_media.created_at is not None

    def test_coach_media_with_image(self):
        """Test creating CoachMedia with image file (default)."""
        coach_media = CoachMediaFactory()

        assert coach_media.file.name.endswith(".jpg")

    def test_coach_media_str_representation(self):
        """Test the string representation of CoachMedia."""
        coach_media = CoachMediaFactory()
        expected_str = f"Coach media - {coach_media.id}"

        assert str(coach_media) == expected_str

    def test_coach_media_relationship(self):
        """Test the relationship between Coach and CoachMedia."""
        coach = CoachFactory()
        coach_media1 = CoachMediaFactory(coach=coach)
        coach_media2 = CoachMediaFactory(coach=coach)

        # Test that coach has multiple media files
        assert coach.media.count() == 2  # noqa: PLR2004
        assert coach_media1 in coach.media.all()
        assert coach_media2 in coach.media.all()

    def test_coach_media_cascade_delete(self):
        """Test that CoachMedia is deleted when Coach is deleted."""
        coach = CoachFactory()
        coach_media = CoachMediaFactory(coach=coach)
        coach_media_id = coach_media.id

        # Delete the coach
        coach.delete()

        # Verify that the coach media is also deleted
        assert not CoachMedia.objects.filter(id=coach_media_id).exists()
