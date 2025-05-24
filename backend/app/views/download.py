# app/views/download.py

import logging
from django.http import HttpResponse
from rest_framework.decorators import api_view
from app.services.download_service import get_file_from_session

logger = logging.getLogger(__name__)


@api_view(["GET"])
def download_file(request):
    try:
        file_data, content_type, filename = get_file_from_session(request.session)

        response = HttpResponse(file_data, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        logger.info(f"{filename} file ready for download")
        return response

    except ValueError as e:
        logger.warning(f"Download failed: {e}")
        return HttpResponse(str(e), status=400)

    except Exception as e:
        logger.exception("Unexpected error during file download")
        return HttpResponse("Unexpected error occurred.", status=500)
