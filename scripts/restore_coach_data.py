import csv
import logging
from pathlib import Path

from django.db import transaction

from coach.models import Category
from coach.models import Coach
from coach.models import SocialMediaLink
from coach.models import SubCategory

logger = logging.getLogger(__name__)


def run():
    """
    Load coach data from CSV file and create or update coach records.
    Updates based on matching first_name and last_name.
    """
    csv_path = Path(__file__).parent / "data" / "coach.csv"

    if not csv_path.exists():
        logger.error("CSV file not found: %s", csv_path)
        return

    created_count = 0
    updated_count = 0
    error_count = 0

    with csv_path.open(encoding="utf-8") as file:
        reader = csv.DictReader(file)

        # Start at 2 since row 1 is header
        for row_num, row in enumerate(reader, start=2):
            try:
                result = _process_coach_row(row, row_num)
                if result == "created":
                    created_count += 1
                elif result == "updated":
                    updated_count += 1
                elif result == "skipped":
                    continue
            except (ValueError, KeyError, TypeError):
                error_count += 1
                first_name = row.get("First Name", "")
                last_name = row.get("Family Name", "")
                logger.exception(
                    "Row %s: Error processing %s %s",
                    row_num,
                    first_name,
                    last_name,
                )

    logger.info("Import completed:")
    logger.info("  Created: %s coaches", created_count)
    logger.info("  Updated: %s coaches", updated_count)
    logger.info("  Errors: %s rows", error_count)


def _process_coach_row(row, row_num):
    """Process a single coach row from CSV."""
    with transaction.atomic():
        # Extract basic coach data
        first_name = row.get("First Name", "").strip()
        last_name = row.get("Family Name", "").strip()

        if not first_name:
            logger.warning("Row %s: Skipping - no first name provided", row_num)
            return "skipped"

        # Find or create coach based on first_name and last_name
        coach, created = Coach.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            defaults=_get_coach_defaults(row),
        )

        if not created:
            # Update existing coach
            _update_coach_fields(coach, row)

        # Handle categories and social media
        _handle_coach_categories(coach, row)
        _handle_social_media_links(coach, row)

        status = "Created" if created else "Updated"
        logger.info("Row %s: %s coach: %s %s", row_num, status, first_name, last_name)
        return "created" if created else "updated"


def _get_coach_defaults(row):
    """Get default values for coach creation."""
    return {
        "title": row.get("Titel", "").strip(),
        "company": row.get("Company", "").strip(),
        "street_no": row.get("Street / No", "").strip(),
        "zip_code": row.get("Zip", "").strip(),
        "city": row.get("City", "").strip(),
        "country": row.get("Country", "").strip(),
        "email": row.get("E-Mail", "").strip(),
        "phone_number": row.get("Phone", "").strip(),
        "website": row.get("Web", "").strip(),
        "about": row.get("About", "").strip(),
        "type": _get_coach_type(row.get("Type", "")),
        "verification_status": _get_verification_status(row.get("Status", "")),
    }


def _update_coach_fields(coach, row):
    """Update existing coach fields."""
    coach.title = row.get("Titel", "").strip()
    coach.company = row.get("Company", "").strip()
    coach.street_no = row.get("Street / No", "").strip()
    coach.zip_code = row.get("Zip", "").strip()
    coach.city = row.get("City", "").strip()
    coach.country = row.get("Country", "").strip()
    coach.email = row.get("E-Mail", "").strip()
    coach.phone_number = row.get("Phone", "").strip()
    coach.website = row.get("Web", "").strip()
    coach.about = row.get("About", "").strip()
    coach.type = _get_coach_type(row.get("Type", ""))
    coach.verification_status = _get_verification_status(row.get("Status", ""))
    coach.save()


def _handle_coach_categories(coach, row):
    """Handle main category and subcategories for coach."""
    # Handle main category
    main_category_name = row.get("Main Category", "").strip()
    if main_category_name:
        category, _ = Category.objects.get_or_create(
            name=main_category_name,
            defaults={"description": f"Category: {main_category_name}"},
        )
        coach.category = category
        coach.save()

    # Handle subcategories
    coach.subcategory.clear()  # Clear existing subcategories
    subcategory_fields = ["Subcategory 1", "Subcategory 2", "Subcategory 3"]
    for subcategory_field in subcategory_fields:
        subcategory_name = row.get(subcategory_field, "").strip()
        if subcategory_name:
            subcategory, _ = SubCategory.objects.get_or_create(
                name=subcategory_name,
                defaults={
                    "description": f"Subcategory: {subcategory_name}",
                    "category": coach.category,
                },
            )
            coach.subcategory.add(subcategory)


def _handle_social_media_links(coach, row):
    """Handle social media links for coach."""
    social_media_data = {
        "instagram": row.get("Instagram", "").strip(),
        "facebook": row.get("Facebook", "").strip(),
        "linkedin": row.get("LinkedIn", "").strip(),
        "youtube": row.get("Youtube", "").strip(),
        "tiktok": row.get("TikTok", "").strip(),
        "x": row.get("X", "").strip(),
        "trustpilot": row.get("Trustpilot", "").strip(),
        "google": row.get("Google", "").strip(),
        "provexpert": row.get("Provenexpert", "").strip(),
    }

    # Remove empty URLs
    social_media_data = {k: v for k, v in social_media_data.items() if v}

    if social_media_data:
        social_media_link, created = SocialMediaLink.objects.get_or_create(
            coach=coach,
            defaults=social_media_data,
        )
        if not created:  # If it already existed, update it
            for field, value in social_media_data.items():
                setattr(social_media_link, field, value)
            social_media_link.save()


def _get_coach_type(type_value):
    """Convert CSV type value to model choice."""
    type_value = type_value.strip().lower()
    if "online" in type_value and "offline" in type_value:
        return Coach.TYPE_ONLINE  # Default to online if both
    if "online" in type_value:
        return Coach.TYPE_ONLINE
    if "offline" in type_value:
        return Coach.TYPE_OFFLINE
    return Coach.TYPE_OFFLINE  # Default


def _get_verification_status(status_value):
    """Convert CSV status value to model choice."""
    status_value = status_value.strip().lower()
    if "verified" in status_value:
        return "verified"
    return "not verified"  # Default
