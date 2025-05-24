# app/views/upload.py

import logging
import json
import numpy as np
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.services.upload_service import handle_upload

logger = logging.getLogger(__name__)


@api_view(["POST"])
def upload_file(request):
    try:
        file = request.FILES["file"]
        logger.debug(f"Received upload request: {file.name}")

        df, preview, columns = handle_upload(file)

        # Save uploaded file format: csv or xlsx
        if file.name.endswith(".xlsx"):
            request.session["uploaded_format"] = "xlsx"
        else:
            request.session["uploaded_format"] = "csv"

        # Save original file
        request.session["uploaded_filename"] = file.name

        # Replace NaN with None for serialization
        safe_data = df.replace({np.nan: None}).to_dict(orient="records")
        request.session["uploaded_data"] = json.dumps(safe_data, default=str)

        preview = df.head(10).replace({np.nan: None}).to_dict("records")

        logger.info(f"Upload successful: {file.name}, columns: {columns}")

        return Response(
            {
                "columns": columns,
                "preview": preview,
                "message": "File uploaded successfully.",
            }
        )

    except ValueError as e:
        logger.warning(f"Upload failed: {e}")
        return Response({"error": str(e)}, status=400)

    except Exception as e:
        logger.exception("Unexpected error during upload")
        return Response({"error": "Unexpected error occurred."}, status=500)
