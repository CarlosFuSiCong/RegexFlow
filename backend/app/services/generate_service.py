# app/services/generate_service.py

import logging
from app.utils.openai_client import get_regex_from_nl

logger = logging.getLogger(__name__)


def generate_regex_from_description(description: str) -> str:
    try:
        logger.debug(f"Generating regex from description: {description}")
        regex = get_regex_from_nl(description)
        logger.info(f"Regex generated: {regex}")
        return regex
    except Exception as e:
        logger.error("Regex generation failed in service layer")
        logger.exception(e)
        raise ValueError("Regex generation failed.")
