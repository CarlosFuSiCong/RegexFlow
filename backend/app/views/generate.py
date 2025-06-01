# app/views/generate.py

import logging
import pandas as pd
from io import StringIO
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.services.generate_service import generate_and_expand_tasks

logger = logging.getLogger(__name__)


@api_view(["POST"])
def generate_regex_tasks(request):
    try:
        description = request.data.get("description")
        if not description:
            logger.warning("Missing description in request.")
            return Response({"error": "Missing description."}, status=400)

        if "working_df" not in request.session:
            logger.warning("No uploaded data found in session.")
            return Response({"error": "No uploaded data found."}, status=400)

        df_json = request.session["working_df"]
        df = pd.read_json(StringIO(df_json))

        tasks = generate_and_expand_tasks(description, df)

        logger.info(f"Regex tasks generated for description: {description}")
        return Response({"tasks": tasks})

    except ValueError as e:
        logger.warning(f"Regex task generation failed: {e}")
        return Response({"error": str(e)}, status=400)

    except Exception as e:
        logger.exception("Unexpected error during regex task generation.")
        return Response({"error": "Unexpected error occurred."}, status=500)
