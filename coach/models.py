import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models

from core.users.models import User


def get_coach_profile_picture_upload_path(instance, filename):
    """
    Generate a unique upload path for the coach's profile picture.
    The path will be in the format: "coaches/profile-pictures/<user_id>/<uuid>_<filename>".
    """  # noqa: E501
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"coaches/profile-pictures/{filename}"


def get_coach_cover_image_upload_path(instance, filename):
    """
    Generate a unique upload path for the coach's cover image.
    The path will be in the format: "coaches/cover-images/<user_id>/<uuid>_<filename>".
    """
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"coaches/cover-images/{filename}"


def get_coach_review_proof_file_upload_path(instance, filename):
    """
    Generate a unique upload path for the coach review proof file.
    The path will be in the format: "coaches/review-proof-files/<user_id>/<uuid>_<filename>".
    """  # noqa: E501
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"coaches/review-proof-files/{filename}"


def get_category_icon_upload_path(instance, filename):
    """
    Generate a unique upload path for the category icon.
    The path will be in the format: "categories/icons/<uuid>_<filename>".
    """
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"coaches/categories/icons/{filename}"


def get_subcategory_icon_upload_path(instance, filename):
    """
    Generate a unique upload path for the subcategory icon.
    The path will be in the format: "subcategories/icons/<uuid>_<filename>".
    """
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"coaches/subcategories/icons/{filename}"


def get_coach_media_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"coaches/media/{filename}"


class Coach(models.Model):
    """
    Model representing a coach.
    """

    TYPE_OFFLINE = "offline"
    TYPE_ONLINE = "online"
    TYPE_ONLINE_OFFLINE = "online_offline"
    TYPE_CHOICES = [
        (TYPE_OFFLINE, "Offline"),
        (TYPE_ONLINE, "Online"),
        (TYPE_ONLINE_OFFLINE, "Online and Offline"),
    ]

    REVIEW_APPROVED = "approved"
    REVIEW_PENDING = "pending"
    REVIEW_REJECTED = "rejected"
    REVIEW_STATUS_CHOICES = [
        (REVIEW_APPROVED, "Approved"),
        (REVIEW_PENDING, "Pending"),
        (REVIEW_REJECTED, "Rejected"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name="coach",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255, blank=True, default="")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(
        max_length=255,
        blank=True,
    )
    profile_picture = models.ImageField(
        upload_to="coaches/profile_pictures/",
        blank=True,
        null=True,
    )
    cover_image = models.ImageField(
        upload_to=get_coach_cover_image_upload_path,
        blank=True,
        null=True,
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_ONLINE_OFFLINE,
    )
    about = models.TextField(
        blank=True,
        default="",
        help_text="A brief description about the coach.",
    )
    company = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="The company or organization the coach is associated with.",
    )
    street_no = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Street number of the coach's location.",
    )
    zip_code = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Zip code of the coach's location.",
    )
    city = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="City of the coach's location.",
    )
    country = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Country of the coach's location.",
    )
    website = models.URLField(
        blank=True,
        help_text="Coach's personal or business website.",
    )
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        related_name="coaches",
        null=True,
        blank=True,
    )
    subcategory = models.ManyToManyField(
        "SubCategory",
        related_name="coaches",
        blank=True,
    )

    verification_status = models.CharField(
        max_length=20,
        choices=[
            ("not verified", "Not Verified"),
            ("verified", "Verified"),
            ("verified plus", "Verified Plus"),
        ],
        default="not verified",
    )
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("expert", "Expert"),
        ],
        default="beginner",
    )
    review_status = models.CharField(
        choices=REVIEW_STATUS_CHOICES,
        max_length=20,
        default=REVIEW_PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Coach"
        verbose_name_plural = "Coaches"

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class SavedCoach(models.Model):
    """
    Model representing a saved coach by a user.
    """

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_coaches",
    )
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name="saved_by")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Saved Coach"
        verbose_name_plural = "Saved Coaches"
        unique_together = ("user", "coach")

    def __str__(self):
        return f"{self.user.username} saved {self.coach.first_name} {self.coach.last_name}".strip()  # noqa: E501

    def clean(self):
        """
        Validate that a user cannot save their own coach profile.
        """
        if hasattr(self.user, "coach") and self.user.coach == self.coach:
            from django.core.exceptions import ValidationError

            msg = "Users cannot save their own coach profile."
            raise ValidationError(msg)

    def save(self, *args, **kwargs):  # noqa: DJ012
        self.clean()
        super().save(*args, **kwargs)


class ClaimCoachRequest(models.Model):
    """
    Model representing a request to claim a coach profile.
    """

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="claim_requests",
        null=True,
        blank=True,
    )
    coach = models.ForeignKey(
        Coach,
        on_delete=models.CASCADE,
        related_name="claim_requests",
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    country = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    rejection_reason = models.TextField(
        blank=True,
        default="",
        help_text="Reason for rejection, if applicable.",
    )
    approval_reason = models.TextField(
        blank=True,
        default="",
        help_text="Reason for approval, if applicable.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Claim Coach Request"
        verbose_name_plural = "Claim Coach Requests"

    def __str__(self):
        coach_name = f"{self.coach.first_name} {self.coach.last_name}".strip()
        return f"Claim request for {coach_name} by {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        """
        Override the default save method to handle coach-user association when a request is approved.
        When the status is set to STATUS_APPROVED, this method associates the requesting user
        with the coach profile before saving the model instance. Then, it calls the parent's
        save method to persist the changes.
        Args:
            *args: Variable length argument list to pass to the parent save method.
            **kwargs: Arbitrary keyword arguments to pass to the parent save method.
        """  # noqa: E501

        # Set the user to the coach if the request is approved
        if self.status == self.STATUS_APPROVED:
            self.coach.user = self.user
            self.coach.save()

        super().save(*args, **kwargs)

    def clean(self):
        """
        Validates the request object before saving to the database.
        This method performs several validation checks:
        1. Validates coach and user data via private methods.
        2. Ensures a user is associated with the request when approving or rejecting.
        3. Requires a non-empty approval reason when approving a request.
        4. Requires a non-empty rejection reason when rejecting a request.
        Raises:
            ValidationError: If any validation check fails with an appropriate error message.
        """  # noqa: E501

        self._validate_coach()
        self._validate_user()

        if (
            self.status in [self.STATUS_APPROVED, self.STATUS_REJECTED]
            and not self.user
        ):
            msg = "User is required when approving or rejecting a request."
            raise ValidationError(msg)

        if self.status == self.STATUS_APPROVED and not self.approval_reason.strip():
            msg = "Approval reason is required when approving a request."
            raise ValidationError(msg)

        if self.status == self.STATUS_REJECTED and not self.rejection_reason.strip():
            msg = "Rejection reason is required when rejecting a request."
            raise ValidationError(msg)

    def _validate_coach(self):
        """
        Validates if the coach profile is already claimed by a user.
        Raises:
            ValidationError: If the coach profile is already associated with a user account.
        """  # noqa: E501

        if self.coach and self.coach.user is not None:
            msg = "This coach profile is already claimed."
            raise ValidationError(msg)

    def _validate_user(self):
        """
        Validates that the user does not already have a coach profile.
        This internal validation method checks if the associated user already has a coach profile
        and raises a ValidationError if one exists. This prevents a user from having multiple
        coach profiles.
        Raises:
            ValidationError: If the associated user already has a coach profile.
        """  # noqa: E501

        if self.user and hasattr(self.user, "coach") and self.user.coach:
            msg = "This user already has a coach profile."
            raise ValidationError(msg)


class CoachReview(models.Model):
    """
    Model representing a review for a coach.
    """

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    coach = models.ForeignKey(
        Coach,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
        blank=True,
    )

    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )
    comment = models.TextField(blank=True)
    date = models.DateField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    proof_file = models.FileField(
        upload_to=get_coach_review_proof_file_upload_path,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    rejection_reason = models.TextField(
        blank=True,
        default="",
        help_text="Reason for rejection, if applicable.",
    )
    approval_reason = models.TextField(
        blank=True,
        default="",
        help_text="Reason for approval, if applicable.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Coach Review"
        verbose_name_plural = "Coach Reviews"

    def __str__(self):
        coach_name = f"{self.coach.first_name} {self.coach.last_name}".strip()
        return f"Review for {coach_name} by {self.first_name} {self.last_name}"

    def clean(self):
        if self.status == self.STATUS_APPROVED and not self.approval_reason.strip():
            msg = "Approval reason is required when approving a review."
            raise ValidationError(msg)

        if self.status == self.STATUS_REJECTED and not self.rejection_reason.strip():
            msg = "Rejection reason is required when rejecting a review."
            raise ValidationError(msg)


class SocialMediaLink(models.Model):
    """
    Model representing a social media link for a coach.
    """

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    coach = models.OneToOneField(
        Coach,
        on_delete=models.CASCADE,
        related_name="social_media_links",
    )
    instagram = models.URLField(
        blank=True,
        help_text="Instagram profile link",
    )
    facebook = models.URLField(
        blank=True,
        help_text="Facebook profile link",
    )
    linkedin = models.URLField(
        blank=True,
        help_text="LinkedIn profile link",
    )
    youtube = models.URLField(
        blank=True,
        help_text="YouTube channel link",
    )
    tiktok = models.URLField(
        blank=True,
        help_text="TikTok profile link",
    )
    x = models.URLField(
        blank=True,
        help_text="X (formerly Twitter) profile link",
    )
    trustpilot = models.URLField(
        blank=True,
        help_text="Trustpilot profile link",
    )
    google = models.URLField(
        blank=True,
        help_text="Google profile link",
    )
    provexpert = models.URLField(
        blank=True,
        help_text="ProvExpert profile link",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Social Media Link"
        verbose_name_plural = "Social Media Links"

    def __str__(self):
        return (
            f"{self.coach.first_name} {self.coach.last_name} Social Media Links".strip()
        )


class Category(models.Model):
    """
    Model representing a category for coaches.
    """

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    icon = models.FileField(
        upload_to=get_category_icon_upload_path,
        blank=True,
        null=True,
        help_text="Icon for the category.",
    )
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """
    Model representing a subcategory for coaches.
    """

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    icon = models.FileField(
        upload_to=get_subcategory_icon_upload_path,
        blank=True,
        null=True,
        help_text="Icon for the subcategory.",
    )
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories",
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SubCategory"
        verbose_name_plural = "SubCategories"

    def __str__(self):
        return self.name


class CoachMedia(models.Model):
    coach = models.ForeignKey(
        Coach,
        on_delete=models.CASCADE,
        related_name="media",
    )
    file = models.FileField(
        upload_to=get_coach_media_upload_path,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Coach media - {self.id}"
