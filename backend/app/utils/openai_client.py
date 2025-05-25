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
    Parse a natural language instruction and extract multiple regex-based editing tasks
    for Excel data.

    The function supports complex instructions that include multiple changes,
    and returns each change as a separate task.

    Args:
        description (str): A plain English instruction containing one or more edit requests.
            Example:
            "Replace phone numbers in column Contact with [hidden] and redact all emails in cell B2."

    Returns:
        List[Dict[str, str]]: A list of dictionaries, where each dictionary represents one edit task with:
            - "target": The region in the Excel sheet to apply the change.
                        Can be "cell B2", "column Contact", "row 1", or "all".
            - "regex": The regular expression pattern to search for.
                       No quotes, no explanation, just the raw pattern.
            - "replacement": The string to replace the matched pattern with.
                             May be an empty string if not specified.
            Example return:
            [
                {
                    "target": "column Contact",
                    "regex": "\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b",
                    "replacement": "[hidden]"
                },
                {
                    "target": "cell B2",
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
- target: where to apply the change (e.g., "cell B2", "column Email", "row 0", "all")
- regex: the pattern to match (no quotes)
- replacement: the replacement string (can be empty)

If a field like "Email" is mentioned with specific rows (e.g. "first 3 rows of Email"), convert to:
"cell Email row 0", "cell Email row 1", etc.

Return only a raw JSON array. Do not use markdown syntax like ```json.
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
