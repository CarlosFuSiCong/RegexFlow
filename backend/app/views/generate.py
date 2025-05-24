# app/views/generate.py

import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.services.generate_service import generate_regex_from_description

logger = logging.getLogger(__name__)


@api_view(["POST"])
def generate_regex(request):
    try:
        description = request.data.get("description")

        if not description:
            logger.warning("Missing description in request.")
            return Response({"error": "Missing description."}, status=400)

        regex = generate_regex_from_description(description)

        logger.info(f"Regex generated for description: {description}")
        return Response({"regex": regex})

    except ValueError as e:
        logger.warning(f"Regex generation failed: {e}")
        return Response({"error": str(e)}, status=400)

    except Exception as e:
        logger.exception("Unexpected error during regex generation.")
        return Response({"error": "Unexpected error occurred."}, status=500)
