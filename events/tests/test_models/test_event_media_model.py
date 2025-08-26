from io import BytesIO
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from coach.models import Coach
from coach.tests.factories import CoachFactory
from events.models import EventMedia
from events.tests.factories import EventFactory


class TestEventMedia(TestCase):
    """Tests for the EventMedia model."""

    def setUp(self):
        """Set up test data with one event and 10 media files."""
        # Use coach type constant instead of CoachType model
        self.coach_type = Coach.TYPE_ONLINE

        # Create a coach
        self.coach = CoachFactory(type=self.coach_type)

        # Create an event using EventFactory
        self.event = EventFactory(coach=self.coach)

        # Create 10 media files for the event
        self.media_files = []
        for i in range(10):
            # Alternate between PDF and image files
            if i % 2 == 0:
                file = self._create_test_file(f"event_doc_{i}.pdf")
            else:
                file = self._create_test_image(f"event_image_{i}.jpg")

            media = EventMedia.objects.create(
                event=self.event,
                file=file,
            )
            self.media_files.append(media)

    def _create_test_file(self, filename="test.pdf", content=b"test content"):
        """Helper method to create a test file."""
        return SimpleUploadedFile(
            name=filename,
            content=content,
            content_type="application/pdf",
        )

    def _create_test_image(
        self,
        filename="test.jpg",
        size=(100, 100),
        color="blue",
    ):
        """Helper method to create a test image file."""
        image_file = BytesIO()
        image = Image.new("RGB", size=size, color=color)
        image.save(image_file, "JPEG")
        image_file.seek(0)

        return SimpleUploadedFile(
            name=filename,
            content=image_file.read(),
            content_type="image/jpeg",
        )

    def test_event_media_creation(self):
        """Test creating event media."""
        # Verify we have 10 media objects
        assert EventMedia.objects.filter(event=self.event).count() == 10  # noqa: PLR2004

        # Test creating a new media file
        new_media = EventMedia.objects.create(
            event=self.event,
            file=self._create_test_file("additional_file.pdf"),
        )

        assert new_media.event == self.event
        assert new_media.file is not None
        assert new_media.created_at is not None
        assert EventMedia.objects.filter(event=self.event).count() == 11  # noqa: PLR2004

    def test_string_representation(self):
        """Test string representation of event media."""
        media = self.media_files[0]
        expected_str = f"{self.event.name} - {media.file.name}"
        assert str(media) == expected_str

    def test_upload_path(self):
        """Test that media files are uploaded to the correct path."""
        media = self.media_files[0]

        # Check that the file path includes 'events/media/'
        assert "events/media/" in media.file.path

    def test_event_relation(self):
        """Test the relationship with Event model."""
        # Check that the event has all media files
        event_media = self.event.media.all()
        assert event_media.count() == 10  # noqa: PLR2004

        # Verify all media objects are associated with the event
        for media in self.media_files:
            assert media in event_media

    def test_delete_media_file_on_delete(self):
        """Test that the file is deleted from storage when the model is deleted."""
        media = self.media_files[0]
        file_path = media.file.path

        # Verify file exists
        assert Path(file_path).exists()

        # Delete the media
        media.delete()

        # Check that the file has been deleted from storage
        assert not Path(file_path).exists()

        # Verify media count is reduced
        assert EventMedia.objects.filter(event=self.event).count() == 9  # noqa: PLR2004

    def test_bulk_delete(self):
        """Test deleting multiple media files at once."""
        # Get file paths to check later
        file_paths = [media.file.path for media in self.media_files[:5]]

        # Delete first 5 media objects
        EventMedia.objects.filter(
            id__in=[media.id for media in self.media_files[:5]],
        ).delete()

        # Verify media count is reduced
        assert EventMedia.objects.filter(event=self.event).count() == 5  # noqa: PLR2004

        # Verify files were physically deleted
        for path in file_paths:
            assert not Path(path).exists()

    def test_different_file_types(self):
        """Test that different file types can be uploaded."""
        # Check that we have both PDF and image files
        pdf_count = 0
        image_count = 0

        for media in self.media_files:
            if media.file.name.endswith(".pdf"):
                pdf_count += 1
            elif media.file.name.endswith((".jpg", ".jpeg", ".png")):
                image_count += 1

        # We should have 5 PDFs and 5 images based on our setup
        assert pdf_count == 5  # noqa: PLR2004
        assert image_count == 5  # noqa: PLR2004

    def test_created_at_auto_now(self):
        """Test that created_at is automatically set."""
        # All media files should have a created_at timestamp
        for media in self.media_files:
            assert media.created_at is not None
