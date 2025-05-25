# app/views/replace.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.services.replace_service import apply_tasks
import logging
import pandas as pd

logger = logging.getLogger(__name__)


@api_view(["POST"])
def replace_tasks(request):
    """
    POST Body:
    {
        "tasks": [
            {"target": "column Email", "regex": "...", "replacement": "..."},
            {"target": "cell B2", "regex": "...", "replacement": "..."},
            ...
        ]
    }
    """
    try:
        data = request.data
        tasks = data.get("tasks")

        if not tasks or not isinstance(tasks, list):
            return Response({"error": "Missing or invalid 'tasks' array."}, status=400)

        df = request.session.get("working_df")
        if df is None:
            raise ValueError("No DataFrame found in session.")

        df = pd.read_json(df)

        logger.info(f"Starting regex task application: {len(tasks)} tasks")

        replacements = apply_tasks(df, tasks)

        request.session["working_df"] = df.to_json()

        return Response(
            {
                "message": "Tasks applied successfully.",
                "total_replacements": len(replacements),
                "preview": replacements[:10],
            }
        )

    except ValueError as e:
        logger.warning(f"Validation error during multi-task replacement: {e}")
        return Response({"error": str(e)}, status=400)

    except Exception as e:
        logger.exception("Unexpected error during multi-task replacement.")
        return Response({"error": "Unexpected error occurred."}, status=500)
