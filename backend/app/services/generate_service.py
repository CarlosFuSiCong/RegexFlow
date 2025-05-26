# app/services/generate_service.py

import logging
from typing import List, Dict
from app.utils.openai_client import get_regex_tasks_from_nl
from app.utils.task_expander import expand_task
import pandas as pd

logger = logging.getLogger(__name__)


def generate_and_expand_tasks(
    description: str, df: pd.DataFrame
) -> List[Dict[str, str]]:
    """
    Generate regex tasks from NL and expand them to cell-level tasks.
    """
    try:
        logger.debug(f"Generating regex tasks from description: {description}")
        tasks = get_regex_tasks_from_nl(description)
        logger.info(f"Generated {len(tasks)} high-level tasks.")

        expanded_tasks = []
        for task in tasks:
            expanded = expand_task(df, task)
            expanded_tasks.extend(expanded)

        logger.info(f"Expanded to {len(expanded_tasks)} cell-level tasks.")
        return expanded_tasks

    except Exception as e:
        logger.error("Regex task generation or expansion failed.")
        logger.exception(e)
        raise ValueError("Regex task generation or expansion failed.")
