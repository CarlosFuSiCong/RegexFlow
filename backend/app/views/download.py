# app/views/download.py

from django.http import HttpResponse
from rest_framework.decorators import api_view
from app.services.download_service import get_file_from_session
import logging

logger = logging.getLogger(__name__)


@api_view(["GET"])
def download_file(request):
    try:
        # Get custom file name
        custom_filename = request.GET.get("filename")

        file_bytes, mime_type, default_filename = get_file_from_session(request.session)

        # Use a custom name (with extension), otherwise use the default name
        filename = custom_filename or default_filename

        response = HttpResponse(file_bytes, content_type=mime_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.exception("Download failed.")
        return HttpResponse("Internal server error.", status=500)
