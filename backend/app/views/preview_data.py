# app/views/preview_data.py

import logging
import pandas as pd
import numpy as np
from io import StringIO
from rest_framework.decorators import api_view
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(["GET"])
def preview_data(request):
    try:
        # Get the uploaded DataFrame from session
        df_json = request.session.get("working_df")
        if df_json is None:
            return Response({"error": "No working DataFrame found."}, status=400)

        df = pd.read_json(StringIO(df_json))

        # Get pagination parameters from query string
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 50))

        total_rows = len(df)
        total_pages = (total_rows + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = start + page_size

        # Validate pagination range
        if page < 1 or start >= total_rows:
            return Response({"error": "Page out of range."}, status=400)

        # Get current page data and replace NaN with None
        page_data = df.iloc[start:end].replace({np.nan: None}).to_dict("records")

        # Return paginated result
        return Response(
            {
                "data": page_data,
                "page": page,
                "page_size": page_size,
                "total_rows": total_rows,
                "total_pages": total_pages,
            }
        )

    except Exception as e:
        logger.exception("Error occurred in preview_data.")
        return Response({"error": "Internal server error."}, status=500)
