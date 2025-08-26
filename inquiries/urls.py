from django.urls import path

from inquiries.views import CreateGeneralInquiryView

app_name = "inquiries"

urlpatterns = [
    path(
        "general/",
        CreateGeneralInquiryView.as_view(),
        name="create-general-inquiry",
    ),
]
