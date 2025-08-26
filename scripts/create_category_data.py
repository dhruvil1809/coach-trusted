import logging

from coach.models import Category
from coach.models import SubCategory

logger = logging.getLogger(__name__)


def run():
    """
    Load category and subcategory data using get_or_create.
    This script can be run multiple times safely as it uses get_or_create.
    """
    data = {
        "Business": [
            "Financial Planning",
            "Customer Experience",
            "Marketing Strategy",
            "Strategy Development",
            "Sales Optimization",
            "E-commerce",
            "Operations",
            "Startup Coaching",
            "Business Scaling",
            "Exit Planning",
            "Team Building",
            "Franchise Coaching",
            "Leadership",
        ],
        "Personal Development": [
            "Purpose Discovery",
            "Vision Planning",
            "Mindset Coaching",
            "Motivation Coaching",
            "Self-Love Coaching",
            "Habit Tracking",
            "Accountability",
            "Confidence Building",
            "Decision-Making",
            "Time Management",
            "Resilience Training",
            "Clarity Sessions",
            "Goal Setting",
            "Emotional Intelligence",
        ],
        "Leadership": [
            "Motivation Techniques",
            "Conflict Management",
            "Coaching for Leaders",
            "Leading with Empathy",
            "Visionary Thinking",
            "Executive Presence",
            "Strategic Thinking",
            "Cross-Cultural Leadership",
            "Team Leadership",
            "Inclusive Leadership",
            "Decision-Making",
        ],
        "Holistic / Wellness": [
            "Mind-Body Integration",
            "Spiritual Nutrition",
            "Lifestyle Balance",
            "Emotional Healing",
            "Breathwork",
            "Meditation Practices",
        ],
        "Communication": [
            "Persuasive Communication",
            "Public Speaking",
            "Speech Clarity",
            "Body Language",
            "Storytelling",
            "Media Training",
            "Presentation Skills",
        ],
        "Spiritual": [
            "Intuition Development",
            "Faith-Based Coaching",
            "Spiritual Awakening",
            "Mindfulness",
            "Soul Purpose",
            "Chakra Balancing",
            "Meditation",
            "Energy Healing",
        ],
        "Financial": [
            "Wealth Building",
            "Financial Literacy",
            "Financial Independence",
            "Money Mindset",
            "FIRE Coaching",
            "Investment Basics",
        ],
        "Sales": [
            "B2B Sales",
            "Consultative Selling",
            "Lead Generation",
            "Sales Psychology",
            "Sales Funnels",
            "Sales Management",
            "Email Sales",
            "Cold Outreach",
            "Closing Techniques",
            "Objection Handling",
        ],
        "Marketing": [
            "Email Marketing",
            "Affiliate Marketing",
            "Branding",
            "Copywriting",
            "Social Media Strategy",
            "Video Marketing",
            "Product Launches",
            "Influencer Marketing",
            "Ads Strategy",
            "Growth Hacking",
            "Content Marketing",
            "SEO Coaching",
            "Web Funnel Coaching",
        ],
        "Fitness": ["Strength Training", "Functional Training", "Weight Loss"],
        "Trading": ["Trading Psychology", "Risk Management", "Day Trading"],
        "Health": [
            "Stress Management",
            "Lifestyle Changes",
            "Mental Wellness",
            "Gut Health",
            "Hormone Balance",
            "Nutrition Coaching",
            "Chronic Illness",
            "Holistic Health",
            "Disease Prevention",
        ],
        "Relationship": ["Breakup Recovery", "Dating Strategy", "Marriage Counseling"],
        "Career": [
            "Career Clarity",
            "Freelancer Support",
            "Interview Prep",
            "Executive Coaching",
            "Leadership Path Planning",
            "Job Search Strategy",
            "Career Change",
        ],
        "Academic": [
            "Study Skills",
            "Goal Setting for Students",
            "Exam Prep",
            "Concentration Coaching",
            "Test Anxiety Coaching",
        ],
    }

    logger.info("Starting to load categories and subcategories...")

    # Counter for tracking progress
    categories_created = 0
    categories_existing = 0
    subcategories_created = 0
    subcategories_existing = 0

    # Iterate through the data to create categories and subcategories
    for category_name, subcategory_names in data.items():
        # Create or get the category
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={"description": f"Category for {category_name} coaching"},
        )

        if created:
            categories_created += 1
            logger.info("✓ Created category: %s", category_name)
        else:
            categories_existing += 1
            logger.info("→ Category already exists: %s", category_name)

        # Create or get subcategories for this category
        for subcategory_name in subcategory_names:
            subcategory, created = SubCategory.objects.get_or_create(
                name=subcategory_name,
                defaults={
                    "category": category,
                    "description": f"Subcategory for {subcategory_name} coaching",
                },
            )

            if created:
                subcategories_created += 1
                logger.info("  ✓ Created subcategory: %s", subcategory_name)
            else:
                subcategories_existing += 1
                # Update category if subcategory exists but has no category
                if not subcategory.category:
                    subcategory.category = category
                    subcategory.save()
                    logger.info(
                        "  → Updated subcategory category: %s",
                        subcategory_name,
                    )
                else:
                    logger.info("  → Subcategory already exists: %s", subcategory_name)

    # Log summary
    logger.info("%s", "\n" + "=" * 50)
    logger.info("SUMMARY:")
    logger.info("Categories created: %s", categories_created)
    logger.info("Categories already existing: %s", categories_existing)
    logger.info("Subcategories created: %s", subcategories_created)
    logger.info("Subcategories already existing: %s", subcategories_existing)
    logger.info("Total categories: %s", categories_created + categories_existing)
    total_subcategories = subcategories_created + subcategories_existing
    logger.info("Total subcategories: %s", total_subcategories)
    logger.info("%s", "=" * 50)
    logger.info("✅ Script completed successfully!")
