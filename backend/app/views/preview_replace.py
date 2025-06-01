# app/views/preview_replace.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
import logging
import pandas as pd
from app.services.replace_service import preview_tasks

logger = logging.getLogger(__name__)


@api_view(["POST"])
def preview_replace_tasks(request):
    try:
        tasks = request.data.get("tasks")
        if not tasks or not isinstance(tasks, list):
            return Response({"error": "Missing or invalid 'tasks' array."}, status=400)

        df_json = request.session.get("working_df")
        if df_json is None:
            raise ValueError("No DataFrame found in session.")

        df = pd.read_json(df_json)
        diffs = preview_tasks(df, tasks)

        return Response(
            {
                "message": "Preview completed.",
                "total_matches": len(diffs),
                "preview": diffs,
            }
        )

    except ValueError as e:
        logger.warning(f"Preview validation error: {e}")
        return Response({"error": str(e)}, status=400)
    except Exception as e:
        logger.exception("Unexpected error during preview.")
        return Response({"error": "Unexpected error occurred."}, status=500)
