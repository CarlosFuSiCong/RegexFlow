# app/views/replace.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.services.replace_service import apply_tasks
import logging
import pandas as pd
import copy

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

        df_json = request.session.get("working_df")
        if df_json is None:
            raise ValueError("No DataFrame found in session.")

        # Load the original DataFrame from session
        df = pd.read_json(df_json)

        # Make a deep copy to avoid modifying the original DataFrame directly
        original_df = copy.deepcopy(df)

        logger.info(f"Starting regex task application: {len(tasks)} tasks")

        # Apply regex replacements to the copied DataFrame
        replacements = apply_tasks(original_df, tasks)

        # Save the modified DataFrame back to the session
        request.session["working_df"] = original_df.to_json()

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
