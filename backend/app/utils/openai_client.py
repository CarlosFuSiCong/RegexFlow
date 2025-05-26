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

Your task is to extract regex-based edit instructions from the following Excel-related description.

Assume the data is from Australia. For example:
- Phone numbers may start with "+61" or "04"
- Dates follow the "DD/MM/YYYY" format
- Postal codes are 4-digit numbers (e.g., 2000, 3004)
- Business numbers (ABNs) are 11-digit numbers like "12 345 678 901"

For each edit, return a JSON object with:
- target: where to apply the change. It must be one of:
  - "all"                           → entire sheet
  - "row <number>"                 → specific row (e.g., "row 2")
  - "column <name>"               → specific column by name (e.g., "column Email")
  - "cell <Excel-style>"          → specific cell (e.g., "cell B2")
  - "row <number> columns <start> to <end>" → partial row (0-based column indices)
  - "column <name> rows <start> to <end>"   → partial column (0-based row indices)
  - "range <A1>:<C3>"             → Excel-style rectangular region

Interpret common phrases like:
- "first 3 columns of row 2" → "row 2 columns 0 to 2"
- "first 2 rows of column Email" → "column Email rows 0 to 1"
- "first 4 rows" → ["row 0", "row 1", "row 2", "row 3"]

Regex patterns must be written as raw patterns (no quotes or explanation).
Replacements should be strings (may be empty).

Return only a raw JSON array. Do NOT include Markdown formatting or comments.
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
