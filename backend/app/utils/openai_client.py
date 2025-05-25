# app/utils/openai_client.py

from openai import OpenAI
import os
import logging
import json
from typing import List, Dict

logger = logging.getLogger(__name__)

# Retrieve OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY is not set in the environment.")

client = OpenAI(api_key=api_key)

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_regex_tasks_from_nl(description: str) -> List[Dict[str, str]]:
    """
    Parse a natural language instruction and extract regex-based editing tasks for Excel data.

    Each task includes:
    - "target": A semantic description of the region to edit (e.g., "row 2", "column Email", "first 3 columns of row 1").
                Use a helper like `resolve_target()` to convert it into exact DataFrame locations.
    - "regex": A raw regex pattern to match.
    - "replacement": The string to replace matches with (can be empty).

    Args:
        description (str): English instruction with one or more edit requests.

    Returns:
        List[Dict[str, str]]: A list of edit tasks.

    Example:
    [
        {
            "target": "column Contact",
            "regex": "\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b",
            "replacement": "[hidden]"
        },
        {
            "target": "first 2 rows of column Email",
            "regex": "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",
            "replacement": "[redacted]"
        }
    ]
    """
    # Construct a prompt to request a JSON array of edits
    prompt = f"""
You are a smart assistant.

Your task is to extract regex-based edits from Excel editing instructions.

For each edit, return a JSON object with:
- target: where to apply the change.
  It can be:
  - "all"                         → for entire sheet
  - "row 2"                       → for a specific row
  - "column Email"               → for a specific column
  - "cell B2"                    → for a specific cell
  - "row 1 columns 0 to 2"       → for partial row (by column indices)
  - "column Name rows 0 to 4"    → for partial column (by row indices)
  - "range A1:C3"                → for a block region
- regex: the pattern to match (no quotes)
- replacement: the string to replace matches with (can be empty)

Interpret phrases like:
- "first 3 columns of row 2" → as `"row 2 columns 0 to 2"`
- "first 2 rows of column Email" → as `"column Email rows 0 to 1"`

Return only a raw JSON array. Do not include markdown like ```json.
Description: {description}
JSON:
"""

    try:
        logger.debug(f"Sending prompt: {description}")

        # Send prompt to OpenAI API
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,  # Allow enough room for multiple edits
            temperature=0,  # Deterministic output
        )

        content = response.choices[0].message.content.strip()
        logger.info(f"Parsed tasks: {content}")

        return json.loads(content)

    except Exception as e:
        logger.exception("Failed to parse multiple instructions")
        raise ValueError(
            "Could not interpret the description into multiple edit tasks."
        )
