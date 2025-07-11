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
        # Get uploaded file
        file = request.FILES["file"]
        logger.debug(f"Received upload request: {file.name}")

        # Read the file into DataFrame, extract preview and column names
        df, columns = handle_upload(file)

        # Save file format
        if file.name.endswith(".xlsx"):
            request.session["uploaded_format"] = "xlsx"
        else:
            request.session["uploaded_format"] = "csv"

        # Save original filename
        request.session["uploaded_filename"] = file.name

        # Save uploaded data (for original download)
        safe_data = df.replace({np.nan: None}).to_dict(orient="records")
        request.session["uploaded_data"] = json.dumps(safe_data, default=str)

        # Save working DataFrame (used by replace and preview)
        request.session["working_df"] = df.to_json()

        # Generate first-page preview (default page=1, page_size=50)
        page = 1
        page_size = 50
        start = (page - 1) * page_size
        end = start + page_size
        preview = df.iloc[start:end].replace({np.nan: None}).to_dict("records")
        total_rows = len(df)

        logger.info(f"Upload successful: {file.name}, columns: {columns}")

        return Response(
            {
                "columns": columns,
                "preview": preview,
                "page": page,
                "page_size": page_size,
                "total_rows": total_rows,
                "total_pages": (total_rows + page_size - 1) // page_size,
                "message": "File uploaded successfully.",
            }
        )

    except ValueError as e:
        logger.warning(f"Upload failed: {e}")
        return Response({"error": str(e)}, status=400)

    except Exception as e:
        logger.exception("Unexpected error during upload")
        return Response({"error": "Unexpected error occurred."}, status=500)
