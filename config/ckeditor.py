"""
CKEditor 5 configuration and upload functionality for Coach Trusted application.

This module contains all CKEditor 5 related settings, configurations, and views.
"""

import uuid
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# CKEditor 5 Custom Color Palette
CUSTOM_COLOR_PALETTE = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]

# CKEditor 5 Configuration
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": {
            "items": [
                "heading",
                "|",
                "bold",
                "italic",
                "link",
                "bulletedList",
                "numberedList",
                "blockQuote",
                "imageUpload",
            ],
        },
    },
    "extends": {
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": {
            "items": [
                "heading",
                "|",
                "outdent",
                "indent",
                "|",
                "bold",
                "italic",
                "link",
                "underline",
                "strikethrough",
                "code",
                "subscript",
                "superscript",
                "highlight",
                "|",
                "codeBlock",
                "sourceEditing",
                "insertImage",
                "bulletedList",
                "numberedList",
                "todoList",
                "|",
                "blockQuote",
                "imageUpload",
                "|",
                "fontSize",
                "fontFamily",
                "fontColor",
                "fontBackgroundColor",
                "mediaEmbed",
                "removeFormat",
                "insertTable",
            ],
            "shouldNotGroupWhenFull": "true",
        },
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": CUSTOM_COLOR_PALETTE,
                "backgroundColors": CUSTOM_COLOR_PALETTE,
            },
            "tableCellProperties": {
                "borderColors": CUSTOM_COLOR_PALETTE,
                "backgroundColors": CUSTOM_COLOR_PALETTE,
            },
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ],
        },
    },
    "list": {
        "properties": {
            "styles": "true",
            "startIndex": "true",
            "reversed": "true",
        },
    },
}

# CKEditor 5 Upload File View Name
CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME = "custom_upload_file"


@csrf_exempt
@login_required
def custom_upload_view(request):
    # Check if user is staff
    if not request.user.is_staff:
        return JsonResponse(
            {
                "uploaded": 0,
                "error": {
                    "message": "Permission denied. Only staff users can upload files.",
                },
            },
        )

    if request.method == "POST" and request.FILES.get("upload"):
        upload = request.FILES["upload"]

        # Ubah nama file (pakai UUID)
        file_ext = Path(upload.name).suffix
        filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = Path("uploads/ckeditor/") / filename

        saved_path = default_storage.save(str(file_path), ContentFile(upload.read()))
        file_url = default_storage.url(saved_path)

        return JsonResponse({"uploaded": 1, "fileName": filename, "url": file_url})
    return JsonResponse({"uploaded": 0, "error": {"message": "Upload failed"}})
