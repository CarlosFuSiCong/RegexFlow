# app/services/generate_service.py

import logging
from typing import List, Dict
from app.utils.openai_client import get_regex_tasks_from_nl

logger = logging.getLogger(__name__)


def generate_regex_tasks_from_description(description: str) -> List[Dict[str, str]]:
    try:
        logger.debug(f"Generating regex tasks from description: {description}")
        tasks = get_regex_tasks_from_nl(description)
        logger.info(f"Generated {len(tasks)} regex tasks.")
        return tasks
    except Exception as e:
        logger.error("Regex task generation failed in service layer.")
        logger.exception(e)
        raise ValueError("Regex task generation failed.")
