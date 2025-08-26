"""
Django Unfold admin interface configuration for Coach Trusted application.


"""

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD_CONFIG = {
    "SITE_TITLE": "Coach Trusted",
    "SITE_HEADER": "Coach Trusted Admin",
    "SITE_LOGO": lambda request: static("images/logo.png"),
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Dashboard"),
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": "/admin/",
                    },
                ],
            },
            {
                "title": _("Coaches"),
                "collapsible": False,
                "items": [
                    {
                        "title": _("Coaches"),
                        "icon": "sports_motorsports",
                        "link": "/admin/coach/coach/",
                    },
                    {
                        "title": _("Reviews"),
                        "icon": "star",
                        "link": "/admin/coach/coachreview/",
                    },
                    {
                        "title": _("Saved Coaches"),
                        "icon": "bookmark",
                        "link": "/admin/coach/savedcoach/",
                    },
                    {
                        "title": _("Claim Requests"),
                        "icon": "person_add",
                        "link": "/admin/coach/claimcoachrequest/",
                    },
                    {
                        "title": _("Social Media Links"),
                        "icon": "share",
                        "link": "/admin/coach/socialmedialink/",
                    },
                    # {  # noqa: ERA001, RUF100
                    #     "title": _("Coach Media"),  # noqa: ERA001
                    #     "icon": "photo_library",  # noqa: ERA001
                    #     "link": "/admin/coach/coachmedia/",  # noqa: ERA001
                    # },
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": "/admin/coach/category/",
                    },
                    {
                        "title": _("Sub Categories"),
                        "icon": "subdirectory_arrow_right",
                        "link": "/admin/coach/subcategory/",
                    },
                ],
            },
            {
                "title": _("Events"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Events"),
                        "icon": "event",
                        "link": "/admin/events/event/",
                    },
                    {
                        "title": _("Event Media"),
                        "icon": "photo_library",
                        "link": "/admin/events/eventmedia/",
                    },
                    {
                        "title": _("Event Tickets"),
                        "icon": "confirmation_number",
                        "link": "/admin/events/eventticket/",
                    },
                    {
                        "title": _("Event Participants"),
                        "icon": "group",
                        "link": "/admin/events/eventparticipant/",
                    },
                    {
                        "title": _("Saved Events"),
                        "icon": "bookmark",
                        "link": "/admin/events/savedevent/",
                    },
                ],
            },
            {
                "title": _("Products"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Products"),
                        "icon": "inventory",
                        "link": "/admin/products/product/",
                    },
                    {
                        "title": _("Product Types"),
                        "icon": "label",
                        "link": "/admin/products/producttype/",
                    },
                    {
                        "title": _("Product Categories"),
                        "icon": "category",
                        "link": "/admin/products/productcategory/",
                    },
                    {
                        "title": _("Product Media"),
                        "icon": "photo_library",
                        "link": "/admin/products/productmedia/",
                    },
                    {
                        "title": _("Saved Products"),
                        "icon": "bookmark",
                        "link": "/admin/products/savedproduct/",
                    },
                ],
            },
            {
                "title": "Quizzes",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Quizzes"),
                        "icon": "quiz",
                        "link": "/admin/quizzes/quiz/",
                    },
                    {
                        "title": _("Fields"),
                        "icon": "mist",
                        "link": "/admin/quizzes/fields/",
                    },
                ],
            },
            {
                "title": _("User Management"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "account_circle",
                        "link": "/admin/users/user/",
                    },
                    {
                        "title": _("Profiles"),
                        "icon": "person",
                        "link": "/admin/users/profile/",
                    },
                    {
                        "title": _("Verification Codes"),
                        "icon": "verified_user",
                        "link": "/admin/users/verificationcode/",
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": "/admin/auth/group/",
                    },
                ],
            },
            {
                "title": _("Notifications"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Notifications"),
                        "icon": "notifications",
                        "link": "/admin/notifications/notification/",
                    },
                ],
            },
            {
                "title": _("Inquiries"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("General Inquiries"),
                        "icon": "contact_support",
                        "link": "/admin/inquiries/generalinquiry/",
                    },
                ],
            },
            {
                "title": _("Blog"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": "/admin/blogs/category/",
                    },
                    {
                        "title": _("Posts"),
                        "icon": "article",
                        "link": "/admin/blogs/post/",
                    },
                ],
            },
            {
                "title": _("Settings"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Meta Content"),
                        "icon": "settings",
                        "link": "/admin/settings/metacontent/",
                    },
                ],
            },
            {
                "title": _("Authentication"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Tokens"),
                        "icon": "vpn_key",
                        "link": "/admin/authtoken/tokenproxy/",
                    },
                ],
            },
            {
                "title": _("Celery Tasks"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Clocked"),
                        "icon": "hourglass_bottom",
                        "link": reverse_lazy(
                            "admin:django_celery_beat_clockedschedule_changelist",
                        ),
                    },
                    {
                        "title": _("Crontabs"),
                        "icon": "update",
                        "link": reverse_lazy(
                            "admin:django_celery_beat_crontabschedule_changelist",
                        ),
                    },
                    {
                        "title": _("Intervals"),
                        "icon": "timer",
                        "link": reverse_lazy(
                            "admin:django_celery_beat_intervalschedule_changelist",
                        ),
                    },
                    {
                        "title": _("Periodic tasks"),
                        "icon": "task",
                        "link": reverse_lazy(
                            "admin:django_celery_beat_periodictask_changelist",
                        ),
                    },
                    {
                        "title": _("Solar events"),
                        "icon": "event",
                        "link": reverse_lazy(
                            "admin:django_celery_beat_solarschedule_changelist",
                        ),
                    },
                ],
            },
        ],
    },
}
