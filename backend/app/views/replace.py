# app/views/replace.py

import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.services.replace_service import handle_full_table_replacement

logger = logging.getLogger(__name__)


@api_view(["POST"])
def replace_all(request):
    """
    POST Body:
    {
        "regex": "<pattern>",
        "replacement": "<replacement_text>" (optional)
    }
    """
    try:
        data = request.data
        regex = data.get("regex")
        replacement = data.get("replacement", "")

        if not regex:
            return Response({"error": "Missing required field: regex."}, status=400)

        logger.info(
            f"Initiating full table replacement: pattern={regex}, replacement={replacement}"
        )

        result = handle_full_table_replacement(
            session=request.session, pattern=regex, replacement=replacement
        )

        return Response(
            {
                "message": "Replacement completed successfully.",
                "replaced_count": len(result["replacements"]),
                "preview": result["replacements"][:10],
            }
        )

    except ValueError as e:
        logger.warning(f"Validation error during replacement: {e}")
        return Response({"error": str(e)}, status=400)

    except Exception as e:
        logger.exception("Unexpected error during regex replacement.")
        return Response({"error": "Unexpected error occurred."}, status=500)
